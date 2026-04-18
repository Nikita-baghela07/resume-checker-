"""
BERT-based embedder for the Dynamic Resume Tailoring Engine.

Wraps ``bert-base-uncased`` (or any compatible HuggingFace BERT model) and
exposes two embedding granularities:

* **Text → sentence embedding** (``encode`` / ``encode_text``)
  Mean-pool all token representations to produce a single dense vector that
  captures the overall meaning of a sentence or paragraph.  The ``encode``
  method is intentionally signature-compatible with ``SentenceTransformer``
  so that existing callers need no changes.

* **Text → word embeddings** (``encode_words``)
  Return a mapping of {word: contextual_embedding} where each vector is the
  mean of the BERT sub-word token embeddings for that surface form.  These
  contextual vectors can be compared with cosine similarity to detect
  *semantically* similar keywords even when there is no exact or stem match
  (e.g. "developer" ≈ "engineer", "optimise" ≈ "improve").
"""

from __future__ import annotations

import re
import numpy as np

try:
    import torch
    from transformers import BertModel, BertTokenizer
    _TRANSFORMERS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _TRANSFORMERS_AVAILABLE = False


class BertEmbedder:
    """
    Dual-granularity BERT embedder.

    Parameters
    ----------
    model_name:
        Any HuggingFace model identifier for a BERT-architecture model.
        Defaults to ``bert-base-uncased`` (12 layers, 768-dim, ~110 MB).
    max_length:
        Maximum token sequence length passed to the tokeniser.
    """

    def __init__(
        self,
        model_name: str = "bert-base-uncased",
        max_length: int = 512,
    ) -> None:
        if not _TRANSFORMERS_AVAILABLE:
            raise RuntimeError(
                "transformers and torch are required.  "
                "Install them with: pip install transformers torch"
            )
        self.model_name = model_name
        self.max_length = max_length
        self.tokenizer: BertTokenizer = BertTokenizer.from_pretrained(model_name)
        self.model: BertModel = BertModel.from_pretrained(model_name)
        self.model.eval()
        self.hidden_size: int = self.model.config.hidden_size  # 768 for bert-base

    # ── Low-level helpers ─────────────────────────────────────────────────────

    def _run_bert(self, text: str):
        """
        Tokenise *text* and run a single forward pass.

        Returns
        -------
        (token_embeddings, attention_mask, tokens)
            token_embeddings : Tensor[seq_len, hidden_size]
            attention_mask   : Tensor[seq_len]
            tokens           : list[str]  (BERT sub-word tokens including special)
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
            padding=False,
        )
        with torch.no_grad():
            outputs = self.model(**inputs)

        token_embs = outputs.last_hidden_state[0]          # (seq_len, hidden)
        attn_mask  = inputs["attention_mask"][0].float()   # (seq_len,)
        tokens     = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        return token_embs, attn_mask, tokens

    # ── Public API ────────────────────────────────────────────────────────────

    def encode_text(self, text: str) -> np.ndarray:
        """
        Text → sentence embedding via attention-masked mean pooling.

        Returns a 1-D NumPy array of shape ``(hidden_size,)`` (768 for
        ``bert-base-uncased``).
        """
        token_embs, attn_mask, _ = self._run_bert(text)
        # Expand mask to broadcast over hidden dimension
        mask_expanded = attn_mask.unsqueeze(-1).expand(token_embs.size())
        sum_embs  = (token_embs * mask_expanded).sum(dim=0)
        sum_mask  = mask_expanded.sum(dim=0).clamp(min=1e-9)
        sentence_emb = (sum_embs / sum_mask).numpy()        # (hidden_size,)
        return sentence_emb

    def encode(self, texts) -> np.ndarray:
        """
        Sentence-Transformers-compatible interface.

        Parameters
        ----------
        texts : str | list[str]

        Returns
        -------
        np.ndarray of shape ``(n, hidden_size)``
        """
        if isinstance(texts, str):
            texts = [texts]
        return np.vstack([self.encode_text(t) for t in texts])

    def encode_words(self, text: str) -> dict[str, np.ndarray]:
        """
        Text → word-level contextual embeddings.

        BERT tokenises text into sub-word pieces (e.g. "playing" →
        ``["play", "##ing"]``).  This method re-assembles sub-word pieces into
        surface words and averages their embeddings, yielding one vector per
        unique lower-cased word.

        Special tokens ``[CLS]``, ``[SEP]``, and ``[PAD]`` are excluded.

        Parameters
        ----------
        text : str
            Any plain text (resume section, job description, …).

        Returns
        -------
        dict[str, np.ndarray]
            Mapping from lower-cased word → embedding of shape
            ``(hidden_size,)``.
        """
        token_embs, _, tokens = self._run_bert(text)

        word_embeddings: dict[str, list[np.ndarray]] = {}
        current_word = ""

        for token, emb in zip(tokens, token_embs):
            if token in ("[CLS]", "[SEP]", "[PAD]"):
                continue

            emb_np = emb.numpy()

            if token.startswith("##"):
                # Continuation of the previous surface word.
                # Use setdefault so that an orphaned continuation (e.g. after a
                # skipped punctuation token) is still captured rather than lost.
                current_word += token[2:]
                word_embeddings.setdefault(current_word, []).append(emb_np)
            else:
                current_word = token.lower()
                # Skip purely punctuation tokens
                if re.search(r"[a-zA-Z0-9]", current_word):
                    word_embeddings.setdefault(current_word, []).append(emb_np)

        # Average sub-word embeddings for each word
        return {
            word: np.mean(np.stack(vecs), axis=0)
            for word, vecs in word_embeddings.items()
            if vecs
        }
