# Sistema de Templates - BidAnalyzee

Sistema de templates reutilizáveis para configurar análises de editais.

## 📋 Visão Geral

Templates permitem salvar e reutilizar configurações de análise para diferentes tipos de licitações, aumentando eficiência e padronização.

## 🎯 Benefícios

- ✅ **Padronização** - Análises consistentes para tipos similares de editais
- ✅ **Eficiência** - Não reconfigurar a cada análise
- ✅ **Customização** - Ajuste fino por domínio/categoria
- ✅ **Rastreabilidade** - Histórico de uso e versão

## 📁 Templates Disponíveis

### 1. TI - Videomonitoramento (`ti_videomonitoramento.yaml`)

**Categoria:** Tecnologia da Informação
**Uso:** Editais de CFTV, videomonitoramento, segurança eletrônica

**Características:**
- Foco em especificações técnicas de câmeras e storage
- Validações para certificações ANATEL e INMETRO
- Categorias esperadas: Hardware, Software, Câmeras, Storage, Rede
- Alertas para requisitos críticos de certificação

**Quando usar:**
- Licitações de videomonitoramento
- Sistemas de CFTV
- Segurança eletrônica com câmeras

### 2. Obras de Engenharia (`obras_engenharia.yaml`)

**Categoria:** Obras
**Uso:** Construção civil, reformas, projetos de engenharia

**Características:**
- Foco em projeto executivo e responsabilidade técnica
- Validações para CREA/CAU e ART/RRT
- Categorias esperadas: Projeto, Materiais, Mão de Obra, Licenças
- Garantia mínima 60 meses
- Timeline/cronograma tracking

**Quando usar:**
- Obras civis
- Reformas
- Projetos de engenharia

### 3. Serviços Gerais (`servicos_gerais.yaml`)

**Categoria:** Serviços
**Uso:** Prestação de serviços diversos, consultoria, manutenção

**Características:**
- Foco em equipe técnica e qualificação
- Validações de SLA e atestados de capacidade
- Categorias esperadas: Escopo, Equipe, Metodologia, SLA
- Flexível para diversos tipos de serviços

**Quando usar:**
- Consultorias
- Serviços de manutenção
- Prestação de serviços gerais

## 🚀 Uso

### Via CLI

```bash
# Listar templates disponíveis
python scripts/template_manager.py list

# Ver detalhes de um template
python scripts/template_manager.py show ti_videomonitoramento

# Criar novo template customizado
python scripts/template_manager.py create

# Deletar template
python scripts/template_manager.py delete meu_template
```

### Via Python

```python
from scripts.template_manager import TemplateManager

# Inicializar
manager = TemplateManager()

# Listar templates
templates = manager.list_templates()
for t in templates:
    print(f"{t['name']}: {t['description']}")

# Carregar template
config = manager.load_template("ti_videomonitoramento")

# Usar configurações
rag_top_k = config['analysis_config']['rag']['top_k']
expected_categories = config['analysis_config']['expected_categories']

# Criar template customizado
custom = manager.create_custom_template(
    name="Minha Categoria",
    description="Template customizado",
    category="custom",
    base_template="ti_videomonitoramento"  # Basear em existente
)

# Salvar
manager.save_template("minha_categoria", custom)
```

### Integração com Análise

```python
# Carregar template
manager = TemplateManager()
template = manager.load_template("ti_videomonitoramento")

# Aplicar configurações RAG
rag_config = template['analysis_config']['rag']
top_k = rag_config['top_k']
threshold = rag_config['similarity_threshold']

# Usar categorias esperadas
expected_cats = template['analysis_config']['expected_categories']

# Alertas
critical_keywords = template['alerts']['critical_keywords']
# Verificar se requisito contém keywords críticas
```

## 📝 Estrutura de Template

```yaml
name: "Nome do Template"
description: "Descrição detalhada"
version: "1.0"
category: "ti"  # ti | obras | servicos | outro
tags:
  - tag1
  - tag2

analysis_config:
  rag:
    top_k: 5
    similarity_threshold: 0.70
    focus_areas:
      - "documento1.md"
      - "documento2.md"

  expected_categories:
    - Categoria1
    - Categoria2

  category_weights:
    Categoria1: 1.5  # Peso maior = mais importante
    Categoria2: 1.2
    default: 1.0

  validations:
    require_certifications:
      - ANATEL
      - INMETRO
    require_technical_specs: true
    require_warranties: true
    minimum_warranty_months: 36

export_config:
  pdf:
    include_diagrams: true
    highlight_critical: true
    group_by_category: true

  excel:
    freeze_panes: true
    conditional_formatting: true
    charts:
      - conformity_pie
      - category_distribution

alerts:
  critical_keywords:
    - "palavra crítica 1"
    - "palavra crítica 2"

  warning_keywords:
    - "aviso 1"
    - "aviso 2"

additional_checks:
  - name: "Nome da verificação"
    category: "Categoria"
    importance: "critical"  # critical | high | medium | low

metadata:
  created_at: "2025-11-16"
  created_by: "Nome"
  last_updated: "2025-11-16"
  use_count: 0
```

## 🛠️ Criar Template Customizado

### Método 1: A partir do zero

```bash
python scripts/template_manager.py create
```

Responda as perguntas interativamente e edite o arquivo YAML gerado.

### Método 2: Copiar existente

```bash
# Copiar arquivo
cp data/templates/ti_videomonitoramento.yaml data/templates/meu_template.yaml

# Editar
nano data/templates/meu_template.yaml

# Ajustar name, description, configs
```

### Método 3: Programaticamente

```python
manager = TemplateManager()

# Basear em template existente
template = manager.create_custom_template(
    name="TI - Redes e Telecomunicações",
    description="Template para editais de redes e telecom",
    category="ti",
    base_template="ti_videomonitoramento"
)

# Customizar
template['analysis_config']['expected_categories'] = [
    'Switches', 'Roteadores', 'Cabeamento', 'Fibra Óptica'
]
template['alerts']['critical_keywords'] = [
    'certificação ANATEL', 'homologação'
]

# Salvar
manager.save_template("ti_redes", template)
```

## 📊 Campos Importantes

### RAG Configuration

- **top_k**: Quantos resultados buscar (recomendado: 3-7)
- **similarity_threshold**: Threshold mínimo de similaridade (0-1)
- **focus_areas**: Documentos prioritários na base de conhecimento

### Category Weights

Quanto maior o peso, mais importante a categoria:
- **1.5+**: Crítico (ex: certificações obrigatórias)
- **1.2-1.4**: Alta importância
- **1.0**: Importância normal
- **< 1.0**: Menos crítico

### Importance Levels

Para `additional_checks`:
- **critical**: Elimina empresa se não atendido
- **high**: Muito importante, mas não eliminatório
- **medium**: Desejável
- **low**: Opcional

## 🔄 Versionamento

Templates suportam versionamento:

```yaml
version: "1.0"  # Inicial
version: "1.1"  # Pequenas mudanças
version: "2.0"  # Mudanças significativas
```

Ao atualizar:
1. Incremente `version`
2. Atualize `metadata.last_updated`
3. Documente mudanças em comentário YAML

## 📈 Estatísticas de Uso

```python
manager = TemplateManager()
stats = manager.get_template_stats("ti_videomonitoramento")

print(f"Usado {stats['use_count']} vezes")
print(f"Última atualização: {stats['last_updated']}")
print(f"{stats['num_expected_categories']} categorias esperadas")
```

O campo `use_count` incrementa automaticamente cada vez que o template é usado.

## 🎯 Boas Práticas

### 1. Nomenclatura Clara

```
✅ ti_videomonitoramento.yaml
✅ obras_construcao_civil.yaml
✅ servicos_limpeza_predial.yaml

❌ template1.yaml
❌ config.yaml
❌ test.yaml
```

### 2. Descrições Completas

```yaml
# ✅ Bom
description: "Template para análise de editais de videomonitoramento, CFTV e segurança eletrônica com câmeras IP"

# ❌ Ruim
description: "Template de vídeo"
```

### 3. Tags Úteis

```yaml
tags:
  - videomonitoramento
  - cftv
  - seguranca-eletronica
  - cameras
  - ti
```

### 4. Manter Atualizado

- Revise templates após cada análise
- Adicione keywords críticas descobertas
- Ajuste pesos de categorias conforme experiência

### 5. Backup

```bash
# Backup periódico
tar -czf templates_backup_$(date +%Y%m%d).tar.gz data/templates/
```

## ⚙️ Integração Futura

Templates podem ser integrados com:

- **Modo FLOW**: Seleção automática de template por categoria
- **Análise**: Aplicar configurações automaticamente
- **Exports**: Customizar formato de saída
- **Dashboard**: Estatísticas por template
- **API**: Endpoints REST para gerenciar templates

## 🐛 Troubleshooting

### "Template not found"

Verifique nome do arquivo:
```bash
ls data/templates/
```

### "Invalid YAML"

Valide sintaxe:
```bash
python -c "import yaml; yaml.safe_load(open('data/templates/seu_template.yaml'))"
```

### "Missing required fields"

Templates devem ter pelo menos:
- `name`
- `description`
- `category`
- `analysis_config`

## 📚 Referências

- [Template Manager Script](../../scripts/template_manager.py)
- [Exemplo: TI Videomonitoramento](ti_videomonitoramento.yaml)
- [Exemplo: Obras](obras_engenharia.yaml)
- [Exemplo: Serviços](servicos_gerais.yaml)

---

**Última atualização:** 16/11/2025
**Versão:** 1.0
