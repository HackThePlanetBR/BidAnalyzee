"""
Embeddings Manager for RAG system

Supports:
- sentence-transformers (local, free, multilingual) - current implementation
- OpenAI embeddings (cloud, paid, high quality) - future migration

Architecture allows easy switching between implementations by changing config.
"""

from typing import List, Literal
from pathlib import Path


class EmbeddingsManager:
    """
    Manages embeddings generation with multiple providers

    Supports both local (sentence-transformers) and cloud (OpenAI) providers.
    Configuration determines which provider to use.
    """

    def __init__(
        self,
        provider: Literal["local", "openai"] = "local",
        model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize embeddings manager

        Args:
            provider: "local" (sentence-transformers) or "openai"
            model: Model name
                - local: "all-MiniLM-L6-v2" (384 dim, fast)
                        "paraphrase-multilingual-mpnet-base-v2" (768 dim, better quality)
                - openai: "text-embedding-3-small" (1536 dim)
        """
        self.provider = provider
        self.model = model
        self.embedder = None
        self.dimension = None

        self._initialize_embeddings()

    def _initialize_embeddings(self) -> None:
        """Initialize the embeddings model based on provider"""
        if self.provider == "local":
            self._initialize_local()
        elif self.provider == "openai":
            self._initialize_openai()
        else:
            raise ValueError(f"Unknown embeddings provider: {self.provider}")

    def _initialize_local(self) -> None:
        """Initialize sentence-transformers (local embeddings)"""
        try:
            from sentence_transformers import SentenceTransformer

            print(f"🔄 Loading local embeddings model: {self.model}")
            print("   (First time may take a few minutes to download model...)")

            self.embedder = SentenceTransformer(self.model)

            # Get embedding dimension
            self.dimension = self.embedder.get_sentence_embedding_dimension()

            print(f"✅ Local embeddings loaded successfully!")
            print(f"   Model: {self.model}")
            print(f"   Dimension: {self.dimension}")
            print(f"   Device: {self.embedder.device}")

        except ImportError:
            print("❌ sentence-transformers not installed. Run: pip install sentence-transformers")
            raise
        except Exception as e:
            print(f"❌ Error loading local embeddings: {e}")
            raise

    def _initialize_openai(self) -> None:
        """Initialize OpenAI embeddings (cloud, future)"""
        try:
            from openai import OpenAI
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found in environment. "
                    "Set it in .env file or export OPENAI_API_KEY=your-key"
                )

            self.embedder = OpenAI(api_key=api_key)

            # Set dimension based on model
            dimension_map = {
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072,
                "text-embedding-ada-002": 1536,
            }
            self.dimension = dimension_map.get(self.model, 1536)

            print(f"✅ OpenAI embeddings initialized!")
            print(f"   Model: {self.model}")
            print(f"   Dimension: {self.dimension}")

        except ImportError:
            print("❌ OpenAI SDK not installed. Run: pip install openai")
            raise
        except Exception as e:
            print(f"❌ Error initializing OpenAI embeddings: {e}")
            raise

    def embed_documents(self, texts: List[str], show_progress: bool = True) -> List[List[float]]:
        """
        Generate embeddings for multiple documents

        Args:
            texts: List of text documents to embed
            show_progress: Show progress bar (only for local)

        Returns:
            List of embedding vectors (one per text)
        """
        if not texts:
            return []

        if self.provider == "local":
            return self._embed_documents_local(texts, show_progress)
        elif self.provider == "openai":
            return self._embed_documents_openai(texts)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _embed_documents_local(self, texts: List[str], show_progress: bool) -> List[List[float]]:
        """Embed documents using sentence-transformers"""
        try:
            print(f"🔄 Generating embeddings for {len(texts)} documents...")

            embeddings = self.embedder.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=show_progress,
                batch_size=32  # Process in batches for efficiency
            )

            # Convert numpy arrays to Python lists
            embeddings_list = embeddings.tolist()

            print(f"✅ Generated {len(embeddings_list)} embeddings")

            return embeddings_list

        except Exception as e:
            print(f"❌ Error generating local embeddings: {e}")
            raise

    def _embed_documents_openai(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using OpenAI API"""
        try:
            print(f"🔄 Generating OpenAI embeddings for {len(texts)} documents...")

            # OpenAI has a limit of ~8000 tokens per request
            # For large batches, we'd need to split into chunks
            # For MVP, assuming reasonable batch sizes

            embeddings = []

            for i, text in enumerate(texts):
                response = self.embedder.embeddings.create(
                    input=text,
                    model=self.model
                )
                embedding = response.data[0].embedding
                embeddings.append(embedding)

                if (i + 1) % 10 == 0:
                    print(f"   Progress: {i + 1}/{len(texts)}")

            print(f"✅ Generated {len(embeddings)} OpenAI embeddings")

            return embeddings

        except Exception as e:
            print(f"❌ Error generating OpenAI embeddings: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        if not text:
            raise ValueError("Query text cannot be empty")

        if self.provider == "local":
            return self._embed_query_local(text)
        elif self.provider == "openai":
            return self._embed_query_openai(text)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _embed_query_local(self, text: str) -> List[float]:
        """Embed query using sentence-transformers"""
        try:
            embedding = self.embedder.encode(
                text,
                convert_to_numpy=True
            )

            return embedding.tolist()

        except Exception as e:
            print(f"❌ Error generating local query embedding: {e}")
            raise

    def _embed_query_openai(self, text: str) -> List[float]:
        """Embed query using OpenAI API"""
        try:
            response = self.embedder.embeddings.create(
                input=text,
                model=self.model
            )

            return response.data[0].embedding

        except Exception as e:
            print(f"❌ Error generating OpenAI query embedding: {e}")
            raise

    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension

    def get_info(self) -> dict:
        """Get information about the embeddings manager"""
        return {
            "provider": self.provider,
            "model": self.model,
            "dimension": self.dimension,
            "device": str(self.embedder.device) if hasattr(self.embedder, "device") else "cloud"
        }


if __name__ == "__main__":
    # Test embeddings manager
    print("Testing Embeddings Manager...")
    print("=" * 60)

    try:
        # Test local embeddings
        manager = EmbeddingsManager(provider="local", model="all-MiniLM-L6-v2")

        print("\n📊 Info:", manager.get_info())

        # Test single query
        print("\n🧪 Testing single query embedding...")
        query = "What are the requirements for technical qualification?"
        query_embedding = manager.embed_query(query)
        print(f"   Query: {query}")
        print(f"   Embedding dimension: {len(query_embedding)}")
        print(f"   First 5 values: {query_embedding[:5]}")

        # Test batch documents
        print("\n🧪 Testing batch document embeddings...")
        documents = [
            "Lei 8.666/93 regulates public procurement in Brazil",
            "Technical qualifications must include CREA registration",
            "Proposals must be submitted within the specified deadline"
        ]
        doc_embeddings = manager.embed_documents(documents, show_progress=False)
        print(f"   Documents: {len(documents)}")
        print(f"   Embeddings: {len(doc_embeddings)}")
        print(f"   Each embedding dimension: {len(doc_embeddings[0])}")

        print("\n✅ All tests passed!")

    except ImportError as e:
        print(f"\n⚠️  Dependencies not installed yet: {e}")
        print("   This is normal during initial setup.")
        print("   Run: pip install sentence-transformers")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
