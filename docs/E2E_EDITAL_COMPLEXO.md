# Sprint 10.5 - Teste E2E com Edital Real Complexo

**Data de Criação:** 15 de novembro de 2025
**Status:** 🔄 EM PROGRESSO
**Prioridade:** 🔥 CRÍTICA

---

## 📋 Contexto e Motivação

### Problema Identificado

Até o Sprint 10, todos os testes foram realizados com **editais simples e curtos**:
- Poucos itens (1-3 itens)
- Requisitos lineares e diretos
- Sem estrutura complexa de subitens
- Arquivos pequenos (< 20 páginas)

**Editais reais são muito mais complexos:**
- ✅ Múltiplos itens (câmeras, servidores, software, switches, etc.)
- ✅ Dezenas ou centenas de requisitos por item
- ✅ Subrequisitos aninhados (requisito → subrequisito → detalhamento)
- ✅ Documentos extensos (100+ páginas)
- ✅ Tabelas complexas com múltiplas colunas
- ✅ Requisitos distribuídos em várias seções do edital

### Objetivo do Sprint 10.5

**Validar e adaptar o sistema para trabalhar com editais complexos reais**, garantindo que:

1. **Extração completa**: Todos os itens e requisitos são capturados
2. **Organização escalável**: Suporte para múltiplos itens/seções
3. **Controle do usuário**: Seleção de quais itens analisar
4. **Validação robusta**: Agente verifica completude vs documento original
5. **Outputs organizados**: Relatórios separados por item quando necessário

---

## 🎯 Objetivos Específicos

### Objetivo 1: Testar Sistema Atual
- Executar workflow completo com `edital.pdf` (edital real complexo)
- Identificar limitações e problemas
- Documentar findings detalhadamente

### Objetivo 2: Implementar Suporte Multi-Item
- Adaptar extração para gerar múltiplos CSVs (1 por item)
- Estrutura: `data/e2e_tests/edital_complexo/item_01_cameras.csv`, `item_02_servidores.csv`, etc.
- Análise de conformidade para cada CSV separadamente
- Exports (PDF/Excel) consolidados ou por item

### Objetivo 3: Seleção Interativa de Itens
- Fase de análise inicial do PDF
- Listar todos os itens disponíveis no edital
- Interface de seleção para usuário escolher:
  - Analisar todos os itens
  - Selecionar itens específicos (menu numerado)
- Workflow adaptado para processar apenas selecionados

### Objetivo 4: Validação Agente vs Original
- Após extração, agente compara CSV(s) gerado(s) com PDF original
- Checklist de validação:
  - Todos os itens do edital foram extraídos?
  - Número de requisitos por item está correto?
  - Nenhum requisito foi esquecido?
  - Informações críticas (obrigatório/opcional, pontuação) foram capturadas?

---

## 📂 Estrutura de Pastas para Testes

```
data/
└── e2e_tests/                         # Pasta dedicada aos testes E2E
    └── edital_complexo/               # Teste com edital real complexo
        ├── input/
        │   └── edital.pdf             # PDF do edital (copiado da raiz)
        ├── extraction/                # Resultados da extração
        │   ├── item_01_cameras.csv
        │   ├── item_02_servidores.csv
        │   ├── item_03_vms.csv
        │   ├── item_04_switches.csv
        │   └── extraction_summary.json  # Resumo: quais itens, quantos requisitos
        ├── analysis/                  # Resultados da análise
        │   ├── item_01_cameras_analysis.csv
        │   ├── item_02_servidores_analysis.csv
        │   ├── item_03_vms_analysis.csv
        │   └── item_04_switches_analysis.csv
        ├── reports/                   # Relatórios finais
        │   ├── relatorio_completo.pdf       # Consolidado
        │   ├── relatorio_completo.xlsx      # Consolidado
        │   ├── relatorio_cameras.pdf        # Por item (opcional)
        │   ├── relatorio_servidores.pdf
        │   └── ...
        ├── validation/                # Validações
        │   └── validation_report.md   # Agente valida se tudo foi extraído
        └── logs/                      # Logs de execução
            └── test_execution.log
```

**Princípio:** Tudo isolado em `data/e2e_tests/edital_complexo/` para não misturar com código ou outros testes.

---

## 🔬 Plano de Teste Detalhado

### Fase 1: Preparação (ATUAL)
**Status:** ✅ Completo
**Atividades:**
- [x] Criar documento de planejamento (este arquivo)
- [x] Atualizar README e ROADMAP
- [ ] Verificar presença de `edital.pdf` na raiz
- [ ] Criar estrutura de pastas `data/e2e_tests/edital_complexo/`
- [ ] Copiar `edital.pdf` para `data/e2e_tests/edital_complexo/input/`

---

### Fase 2: Teste com Sistema Atual
**Status:** ⏳ Pendente
**Objetivo:** Entender como sistema atual se comporta

#### 2.1 Extração
**Comando:**
```bash
# Tentar extrair com sistema atual
/structure-edital data/e2e_tests/edital_complexo/input/edital.pdf
```

**Observações esperadas:**
- ❌ Provável: CSV único enorme e difícil de gerenciar
- ❌ Possível: Perda de alguns requisitos por complexidade
- ❌ Possível: Estrutura inadequada para múltiplos itens

**Documentar:**
- Quanto tempo levou?
- Quantas linhas no CSV?
- CSV está organizado? Legível?
- Algum item foi perdido?

#### 2.2 Análise (se extração funcionar)
**Comando:**
```bash
# Tentar analisar CSV extraído
/analyze-edital <caminho-do-csv-gerado>
```

**Observações esperadas:**
- ⏱️ Tempo de análise (pode ser muito longo)
- 📊 Qualidade da análise
- 🔍 Relatórios gerados funcionam?

**Documentar:**
- Análise completou?
- Tempo total?
- Outputs (PDF/Excel) são utilizáveis?
- Algum erro ou warning?

---

### Fase 3: Implementar Adaptações
**Status:** ⏳ Pendente
**Objetivo:** Tornar sistema capaz de lidar com editais complexos

#### 3.1 Análise Inicial do Edital
**Criar:** `scripts/analyze_edital_structure.py`

**Funcionalidade:**
- Abrir PDF
- Identificar seções/itens principais
- Detectar padrões (tabelas, listas, numeração)
- Extrair lista de itens do edital

**Output:** JSON com estrutura do edital
```json
{
  "edital_path": "data/e2e_tests/edital_complexo/input/edital.pdf",
  "total_pages": 150,
  "items_found": [
    {
      "item_id": "1.1",
      "item_name": "Câmera IP PTZ Full HD",
      "estimated_requirements": 45,
      "pages": [12, 13, 14, 15]
    },
    {
      "item_id": "2.1",
      "item_name": "Servidor de Armazenamento",
      "estimated_requirements": 32,
      "pages": [18, 19, 20]
    },
    // ... mais itens
  ]
}
```

#### 3.2 Interface de Seleção
**Modificar:** `scripts/analyze_edital_full.py` ou criar wrapper

**Fluxo:**
1. Executar análise inicial do edital
2. Apresentar menu interativo:
   ```
   ================================================================================
   📋 ITENS ENCONTRADOS NO EDITAL
   ================================================================================

   [1] Item 1.1 - Câmera IP PTZ Full HD (≈45 requisitos, páginas 12-15)
   [2] Item 2.1 - Servidor de Armazenamento (≈32 requisitos, páginas 18-20)
   [3] Item 3.1 - Software VMS (≈28 requisitos, páginas 24-26)
   [4] Item 4.1 - Switch PoE 48 portas (≈18 requisitos, páginas 30-31)

   ================================================================================

   Escolha uma opção:
   [T] Analisar TODOS os itens
   [S] Selecionar itens específicos
   [Q] Cancelar

   > _
   ```

3. Se `S`, permitir seleção:
   ```
   Digite os números dos itens separados por vírgula (ex: 1,3,4):
   > 1,2

   ✅ Selecionados:
   - [1] Câmera IP PTZ Full HD
   - [2] Servidor de Armazenamento

   Confirma? [S/n]: _
   ```

4. Processar apenas itens selecionados

#### 3.3 Extração Multi-Item
**Modificar:** `/structure-edital` ou criar `/structure-edital-multi`

**Fluxo:**
- Para cada item selecionado:
  1. Extrair requisitos específicos daquele item
  2. Gerar CSV individual: `item_XX_nome.csv`
  3. Salvar em `extraction/`

**Validação:** Agente compara com PDF original
- Checkpoint: "Verifique se todos os requisitos do Item 1.1 foram extraídos"
- Agente lê PDF e conta requisitos
- Compara com linhas no CSV
- Reporta discrepâncias

**Output:**
- CSVs individuais
- `extraction_summary.json` com estatísticas

#### 3.4 Análise Multi-Item
**Modificar:** `/analyze-edital` para aceitar múltiplos CSVs

**Opções:**
1. Processar cada CSV separadamente (análise paralela)
2. Gerar relatórios individuais ou consolidados
3. Consolidar em Excel com abas por item

#### 3.5 Exports Adaptados
**Modificar:** `export_pdf.py` e `export_excel.py`

**PDF:**
- Opção 1: PDF consolidado com seções por item
- Opção 2: PDFs separados por item

**Excel:**
- Aba "Resumo Geral" (todos os itens)
- Aba por item ("Item 1.1 - Câmeras", "Item 2.1 - Servidores", etc.)
- Gráficos consolidados e por item

---

### Fase 4: Teste com Novo Sistema
**Status:** ⏳ Pendente
**Objetivo:** Validar que adaptações funcionam

#### 4.1 Teste Completo
**Executar:**
```bash
python3 scripts/analyze_edital_full.py data/e2e_tests/edital_complexo/input/edital.pdf
```

**Validações:**
1. ✅ Análise inicial funciona
2. ✅ Lista de itens é precisa
3. ✅ Menu de seleção funciona
4. ✅ Extração de múltiplos CSVs funciona
5. ✅ Validação agente vs original detecta problemas
6. ✅ Análise de cada item completa
7. ✅ Relatórios PDF/Excel são gerados corretamente
8. ✅ Outputs são organizados e utilizáveis

#### 4.2 Casos de Teste

**Caso 1: Analisar Todos os Itens**
- Selecionar [T]
- Verificar que todos são processados
- Tempo aceitável?

**Caso 2: Selecionar Itens Específicos**
- Selecionar [S] → 1,3
- Verificar que apenas 1 e 3 são processados
- Outros itens são ignorados

**Caso 3: Validação de Completude**
- Forçar extração incompleta (remover linhas manualmente)
- Executar validação agente
- Verificar que agente detecta discrepância

**Caso 4: Relatórios**
- Verificar PDF consolidado
- Verificar Excel com múltiplas abas
- Verificar se informações estão corretas

---

## 📊 Critérios de Aceitação

### Must-Have (Obrigatório)
- [ ] Sistema consegue extrair edital complexo sem erros críticos
- [ ] Múltiplos CSVs são gerados (1 por item)
- [ ] Interface de seleção funciona corretamente
- [ ] Validação agente vs original está implementada
- [ ] Análise completa de todos os itens selecionados
- [ ] Relatórios PDF e Excel são gerados corretamente
- [ ] Estrutura de pastas organizada (`data/e2e_tests/`)
- [ ] Documentação do teste está completa

### Should-Have (Desejável)
- [ ] Tempo de processamento < 10 minutos para edital completo
- [ ] Relatórios consolidados e por item
- [ ] Logs detalhados de execução
- [ ] Tratamento de erros robusto

### Nice-to-Have (Opcional)
- [ ] Progress bar visual para extração
- [ ] Sugestões de itens similares para análise conjunta
- [ ] Comparação entre itens (se aplicável)

---

## 🚧 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Edital muito complexo para extração automática | Alta | Alto | Implementar validação agente + revisão manual |
| Tempo de processamento muito longo | Média | Médio | Otimizar com processamento paralelo |
| Perda de requisitos na extração | Alta | Alto | Validação agente obrigatória |
| Relatórios muito grandes (não abrem) | Baixa | Médio | Limitar tamanho ou dividir |
| Interface de seleção confusa | Baixa | Baixo | Testes de usabilidade |

---

## 📝 Checklist de Implementação

### Preparação
- [x] Documento de planejamento criado
- [x] README atualizado
- [x] ROADMAP atualizado
- [ ] Estrutura de pastas criada
- [ ] `edital.pdf` verificado e copiado

### Desenvolvimento
- [ ] `scripts/analyze_edital_structure.py` criado
- [ ] Interface de seleção implementada
- [ ] Extração multi-item implementada
- [ ] Validação agente implementada
- [ ] Análise multi-item implementada
- [ ] Exports adaptados (PDF + Excel)

### Testes
- [ ] Teste com sistema atual documentado
- [ ] Teste com novo sistema executado
- [ ] Todos os casos de teste passaram
- [ ] Critérios de aceitação verificados

### Documentação
- [ ] Findings documentados
- [ ] Exemplos de uso adicionados
- [ ] Atualizar ROADMAP com resultados
- [ ] Criar guia de uso para editais complexos

### Finalização
- [ ] Commit das mudanças
- [ ] Push para repositório
- [ ] Tag de versão (v0.10.5)

---

## 📅 Timeline Estimado

| Fase | Atividades | Tempo Estimado | Status |
|------|-----------|----------------|--------|
| 1. Preparação | Documentação + Setup | 1h | ✅ Em andamento |
| 2. Teste Atual | Executar e documentar | 1-2h | ⏳ Pendente |
| 3. Implementação | Código + Adaptações | 6-8h | ⏳ Pendente |
| 4. Testes | Validação completa | 2-3h | ⏳ Pendente |
| 5. Documentação | Finalizar docs | 1h | ⏳ Pendente |
| **TOTAL** | | **11-15h** | |

---

## 🎯 Resultados Esperados

Ao final do Sprint 10.5, o sistema deve ser capaz de:

1. ✅ **Analisar editais reais complexos** sem intervenção manual excessiva
2. ✅ **Gerenciar múltiplos itens** de forma organizada e escalável
3. ✅ **Dar controle ao usuário** sobre quais itens analisar
4. ✅ **Validar completude** automaticamente com agente
5. ✅ **Gerar relatórios profissionais** organizados por item
6. ✅ **Documentar todo o processo** para futuras referências

---

## 📖 Referências

- [ROADMAP.md](../ROADMAP.md) - Roadmap geral do projeto
- [README.md](../README.md) - Visão geral do projeto
- [SPRINT_10_IMPLEMENTATION.md](SPRINT_10_IMPLEMENTATION.md) - Implementação do Sprint 10
- Edital de teste: `edital.pdf` (raiz do projeto)

---

**Mantido por:** Claude + Equipe
**Versão:** 1.0
**Última atualização:** 15/11/2025
