# Guia de Web Scraping para Knowledge Base

**Versão:** 1.0.0
**Data:** 16 de novembro de 2025
**Propósito:** Extrair documentação técnica de sites e popular a knowledge base do RAG

---

## 📋 Visão Geral

Este guia documenta como criar scrapers para extrair artigos de sites de documentação técnica e convertê-los em arquivos Markdown (.md) formatados para o sistema RAG do BidAnalyzee.

---

## 📄 Formato dos Arquivos .md

### Estrutura com Frontmatter YAML

Todos os arquivos .md gerados pelo scraper **devem** incluir frontmatter YAML com os seguintes campos:

```markdown
---
title: "Título Completo do Artigo"
url: "https://docs.exemplo.com/artigos/caminho-completo"
source: "Nome do Site de Documentação"
date: "2025-11-16"
---

# Conteúdo do artigo em Markdown

Texto do artigo aqui...
```

### Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **title** | Título completo do artigo | `"Especificações Técnicas - Processadores Intel Xeon"` |
| **url** | URL completa da página original | `"https://docs.intel.com/processors/xeon-gold-specs"` |
| **source** | Nome da fonte/site | `"Intel ARK - Product Specifications"` |
| **date** | Data da extração (YYYY-MM-DD) | `"2025-11-16"` |

### Campos Opcionais

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **author** | Autor do artigo (se disponível) | `"Intel Corporation"` |
| **category** | Categoria do artigo | `"Hardware"` ou `"Software"` |
| **tags** | Tags/palavras-chave (separadas por vírgula) | `"processador, xeon, servidor, datacenter"` |
| **version** | Versão da documentação (se aplicável) | `"v3.2"` |
| **last_updated** | Data de última atualização no site original | `"2025-10-15"` |

---

## 🔧 Como o Sistema Usa essas Informações

### 1. **Durante a Indexação (RAG Ingestion)**

O `ingestion_pipeline.py` extrai automaticamente o frontmatter:

```python
# Extrai metadata do frontmatter
frontmatter, content = self._extract_frontmatter(raw_content)

doc = {
    "filename": file_path.name,
    "content": content,  # Sem frontmatter
    "title": frontmatter.get("title", file_path.stem),
    "url": frontmatter.get("url", ""),
    "source": frontmatter.get("source", ""),
    "date": frontmatter.get("date", "")
}
```

### 2. **Durante a Busca (RAG Search)**

O `rag_search.py` retorna o metadata com cada resultado:

```json
{
  "query": "processador intel xeon",
  "results": [
    {
      "text": "Processadores Intel Xeon Gold 6XXX ou superior...",
      "similarity_score": 0.92,
      "metadata": {
        "title": "Especificações Técnicas - Processadores",
        "url": "https://docs.intel.com/processors/xeon",
        "filename": "intel_xeon_specs.md",
        "chunk_index": 5
      }
    }
  ]
}
```

### 3. **No CSV de Análise**

As colunas `Fonte_Titulo` e `Fonte_URL` são preenchidas automaticamente:

```csv
ID,Requisito,Categoria,Veredicto,Confiança,Evidências,Raciocínio,Recomendações,Fonte_Titulo,Fonte_URL
1,"Processador Intel Xeon...",Hardware,CONFORME,0.95,"...","...","...","Especificações Técnicas - Processadores","https://docs.intel.com/processors/xeon"
```

---

## 🕷️ Template de Web Scraper

### Exemplo Básico (Python + BeautifulSoup)

```python
#!/usr/bin/env python3
"""
Web Scraper para [Nome do Site de Documentação]

Extrai artigos técnicos e converte para formato .md com frontmatter
compatível com o sistema RAG do BidAnalyzee.
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import re
import time


class TechDocsScraper:
    """Scraper para documentação técnica"""

    def __init__(self, base_url: str, output_dir: str):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Headers para evitar bloqueio
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; BidAnalyzee/1.0; +http://exemplo.com)'
        }

    def slugify(self, text: str) -> str:
        """Converte título em nome de arquivo válido"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text[:100]  # Limita tamanho

    def fetch_page(self, url: str) -> BeautifulSoup:
        """Busca e parseia uma página"""
        print(f"📥 Fetching: {url}")
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'

        return BeautifulSoup(response.text, 'html.parser')

    def extract_article(self, soup: BeautifulSoup, url: str) -> dict:
        """
        Extrai informações do artigo

        IMPORTANTE: Adapte os seletores CSS para o site específico!
        """
        # EXEMPLO - Ajustar para o site real
        title = soup.find('h1', class_='article-title')
        title_text = title.get_text().strip() if title else "Sem Título"

        # Corpo do artigo
        content_div = soup.find('div', class_='article-content')
        if not content_div:
            content_div = soup.find('article')

        if not content_div:
            raise ValueError("Não foi possível encontrar o conteúdo do artigo")

        # Converter HTML para Markdown (simples)
        markdown_content = self.html_to_markdown(content_div)

        # Metadata
        source_name = soup.find('meta', {'property': 'og:site_name'})
        source_text = source_name.get('content') if source_name else "Documentação Técnica"

        return {
            'title': title_text,
            'url': url,
            'source': source_text,
            'content': markdown_content,
            'date': datetime.now().strftime('%Y-%m-%d')
        }

    def html_to_markdown(self, element) -> str:
        """
        Converte HTML para Markdown básico

        Para conversão mais robusta, use bibliotecas como:
        - html2text
        - markdownify
        - pypandoc
        """
        # EXEMPLO SIMPLES - Use biblioteca adequada em produção
        markdown = []

        for tag in element.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'pre', 'code']):
            if tag.name == 'h1':
                markdown.append(f"# {tag.get_text().strip()}\n")
            elif tag.name == 'h2':
                markdown.append(f"## {tag.get_text().strip()}\n")
            elif tag.name == 'h3':
                markdown.append(f"### {tag.get_text().strip()}\n")
            elif tag.name == 'h4':
                markdown.append(f"#### {tag.get_text().strip()}\n")
            elif tag.name == 'p':
                markdown.append(f"{tag.get_text().strip()}\n")
            elif tag.name == 'ul':
                for li in tag.find_all('li', recursive=False):
                    markdown.append(f"- {li.get_text().strip()}")
                markdown.append("")
            elif tag.name == 'ol':
                for i, li in enumerate(tag.find_all('li', recursive=False), 1):
                    markdown.append(f"{i}. {li.get_text().strip()}")
                markdown.append("")
            elif tag.name in ['pre', 'code']:
                code_text = tag.get_text().strip()
                markdown.append(f"```\n{code_text}\n```\n")

        return "\n".join(markdown)

    def save_markdown(self, article: dict):
        """Salva artigo como arquivo .md com frontmatter"""
        # Nome do arquivo
        filename = f"{self.slugify(article['title'])}.md"
        filepath = self.output_dir / filename

        # Frontmatter YAML
        frontmatter = f"""---
title: "{article['title']}"
url: "{article['url']}"
source: "{article['source']}"
date: "{article['date']}"
---

"""

        # Conteúdo completo
        full_content = frontmatter + article['content']

        # Salvar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        print(f"✅ Saved: {filename}")
        return filepath

    def scrape_article(self, url: str):
        """Scrape um único artigo"""
        try:
            soup = self.fetch_page(url)
            article = self.extract_article(soup, url)
            filepath = self.save_markdown(article)

            # Rate limiting - ser educado com o servidor
            time.sleep(2)

            return filepath

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None

    def scrape_index(self, index_url: str, link_selector: str):
        """
        Scrape múltiplos artigos de uma página índice

        Args:
            index_url: URL da página com lista de artigos
            link_selector: Seletor CSS para links dos artigos
        """
        soup = self.fetch_page(index_url)
        links = soup.select(link_selector)

        print(f"\n📚 Found {len(links)} articles to scrape\n")

        for i, link in enumerate(links, 1):
            href = link.get('href')
            if not href.startswith('http'):
                href = self.base_url.rstrip('/') + '/' + href.lstrip('/')

            print(f"\n[{i}/{len(links)}] Processing: {href}")
            self.scrape_article(href)

            # Rate limiting entre artigos
            time.sleep(3)

        print(f"\n✅ Scraping completed! Files saved to: {self.output_dir}")


# Exemplo de uso
if __name__ == "__main__":
    # Configuração - AJUSTAR PARA O SITE REAL
    scraper = TechDocsScraper(
        base_url="https://docs.exemplo.com",
        output_dir="data/knowledge_base/producao"
    )

    # Opção 1: Scrape um artigo único
    scraper.scrape_article("https://docs.exemplo.com/artigos/processadores-xeon")

    # Opção 2: Scrape múltiplos artigos de um índice
    scraper.scrape_index(
        index_url="https://docs.exemplo.com/hardware/indice",
        link_selector="div.article-list a.article-link"  # Ajustar seletor
    )
```

---

## 🎯 Sites Alvo Recomendados

Para documentação de licitações públicas brasileiras:

| Site | Conteúdo | Prioridade |
|------|----------|-----------|
| **Portal da Transparência** | Leis, decretos, portarias | ⭐⭐⭐ |
| **Planalto (LegisWeb)** | Lei 8.666/93, Lei 14.133/2021 | ⭐⭐⭐ |
| **TCU - Tribunal de Contas da União** | Acórdãos, súmulas, jurisprudência | ⭐⭐⭐ |
| **INMETRO** | Normas técnicas, certificações | ⭐⭐ |
| **ANATEL** | Regulamentos telecomunicações | ⭐⭐ |
| **ABNT** | Normas técnicas brasileiras | ⭐⭐ |

---

## ⚙️ Bibliotecas Recomendadas

### Para Scraping

```bash
pip install requests beautifulsoup4 lxml
```

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - Parser rápido

### Para Conversão HTML → Markdown

```bash
pip install html2text markdownify
```

**Exemplo com html2text:**
```python
import html2text

h = html2text.HTML2Text()
h.ignore_links = False
h.ignore_images = False
markdown = h.handle(html_content)
```

### Para Sites JavaScript-heavy

```bash
pip install selenium playwright
```

Se o site usa JavaScript para renderizar conteúdo, use Selenium ou Playwright.

---

## 📊 Depois de Scraping - Indexar no RAG

Após extrair os artigos:

```bash
# 1. Verificar arquivos gerados
ls -lh data/knowledge_base/producao/*.md

# 2. Indexar no RAG
python scripts/index_knowledge_base.py

# 3. Testar busca
python scripts/rag_search.py --requirement "processador intel xeon" --top-k 5
```

---

## ⚠️ Considerações Legais e Éticas

### ✅ Permitido:
- Documentação pública (leis, normas governamentais)
- Sites com termos de uso permitindo scraping educacional/pesquisa
- Conteúdo com licenças abertas (CC-BY, etc.)

### ❌ Evitar:
- Sites com `robots.txt` bloqueando scraping
- Conteúdo protegido por paywall
- Rate muito alto (pode derrubar o servidor)
- Conteúdo protegido por direitos autorais sem permissão

### 🛡️ Boas Práticas:
- Respeite `robots.txt`
- Use User-Agent identificável
- Implemente rate limiting (2-3 segundos entre requests)
- Faça cache local (não re-scrape desnecessariamente)
- Entre em contato com o site se for scraping massivo

---

## 🧪 Testando o Scraper

```python
# test_scraper.py
def test_scraper():
    scraper = TechDocsScraper(
        base_url="https://docs.exemplo.com",
        output_dir="data/knowledge_base/test"
    )

    # Teste com 1 artigo
    filepath = scraper.scrape_article("https://docs.exemplo.com/teste")

    # Verificar frontmatter
    with open(filepath, 'r') as f:
        content = f.read()
        assert content.startswith('---')
        assert 'title:' in content
        assert 'url:' in content
        assert 'source:' in content

    print("✅ Scraper test passed!")

if __name__ == "__main__":
    test_scraper()
```

---

## 📚 Próximos Passos

1. **Identifique os 2 sites alvo** que você quer scraper
2. **Inspecione a estrutura HTML** (DevTools do browser)
3. **Adapte o template acima** com os seletores CSS corretos
4. **Teste com 1 artigo** primeiro
5. **Escale para múltiplos artigos**
6. **Indexe no RAG** e teste a busca

---

## 🆘 Troubleshooting

### Erro: "Não encontrou o conteúdo"
- Verifique os seletores CSS (`soup.find(...)`)
- Use DevTools do navegador para inspecionar HTML
- Site pode usar JavaScript → use Selenium/Playwright

### Erro: "Connection timeout"
- Aumente `timeout` em `requests.get(..., timeout=60)`
- Verifique se site não está bloqueando bot

### Erro: "403 Forbidden"
- Site está bloqueando bots
- Ajuste User-Agent header
- Adicione cookies/session se necessário

### Frontmatter não reconhecido
- Verifique formato YAML (`:` com espaço depois)
- Teste com regex: `^---\s*\n(.*?)\n---\s*\n`

---

**Boa sorte com o scraping! 🕷️**

Lembre-se: seja educado com os servidores alheios e respeite os termos de uso.
