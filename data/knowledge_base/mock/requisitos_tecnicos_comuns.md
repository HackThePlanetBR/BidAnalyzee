# Requisitos Técnicos Comuns em Licitações

**Área:** Especificações Técnicas para Editais
**Aplicação:** Sistemas de Segurança, TI, Infraestrutura, Equipamentos
**Atualização:** Novembro de 2025

---

## Sumário
1. Princípios Gerais de Especificação
2. Requisitos de Hardware
3. Requisitos de Software
4. Requisitos de Rede e Conectividade
5. Requisitos de Segurança
6. Requisitos de Integração
7. Requisitos de Desempenho
8. Requisitos de Suporte e Manutenção
9. Certificações e Conformidades
10. Exemplos Práticos por Categoria

---

## 1. Princípios Gerais de Especificação Técnica

### 1.1 Especificação Adequada (Art. 40, Lei 8.666 e Art. 62, Lei 14.133)

**Requisitos de Boa Especificação:**

✅ **Objetiva e Clara**
- Linguagem técnica precisa
- Termos mensuráveis e verificáveis
- Sem ambiguidades

✅ **Não Restritiva**
- Não citar marcas ou modelos específicos
- Não criar barreiras artificiais à concorrência
- Permitir equivalência técnica

✅ **Completa**
- Todos os requisitos necessários listados
- Condições de aceitação definidas
- Critérios de conformidade explícitos

✅ **Verificável**
- Critérios mensuráveis
- Métodos de teste ou verificação indicados
- Documentação comprobatória definida

### 1.2 Uso de Expressões Permitidas

**✅ CORRETO:**
- "Ou equivalente técnico comprovado"
- "Ou similar de desempenho igual ou superior"
- "Compatível com o padrão/norma X"
- "Deve atender às seguintes especificações mínimas..."

**❌ INCORRETO:**
- "Marca X, modelo Y"
- "Exatamente conforme catálogo Z"
- "Apenas produtos fabricados por..."
- Requisitos que só uma marca atende

### 1.3 Referências a Normas e Padrões

**✅ Permitido e Recomendado:**
- Normas técnicas brasileiras (ABNT)
- Normas internacionais (ISO, IEC, IEEE)
- Padrões de mercado reconhecidos
- Certificações objetivas

**Exemplo Correto:**
```
"O equipamento deve atender às normas:
- ABNT NBR IEC 62676-1 (Sistemas de CFTV)
- IEC 60529 (Grau de proteção IP)
- FCC Part 15 (Interferência eletromagnética)
```

---

## 2. Requisitos de Hardware

### 2.1 Câmeras de Videomonitoramento

**Especificações Mínimas Comuns:**

**Resolução:**
- ✅ Mínimo: **2 Megapixels (1920x1080 - Full HD)**
- ✅ Recomendado: 4 MP ou superior para identificação facial
- ✅ Especificar: "Resolução real, não interpolada"

**Sensor:**
- ✅ Tipo: CMOS progressivo
- ✅ Tamanho: Mínimo 1/2.8"
- ✅ Sensibilidade: 0.01 Lux (cor) ou inferior

**Lente:**
- ✅ Tipo: Varifocal motorizada 2.8-12mm (exemplo)
- ✅ Abertura: F/1.4 ou inferior
- ✅ Controle: Auto-íris
- ✅ Campo de visão: Especificar ângulo necessário (ex: 90° horizontal)

**Taxa de Quadros (FPS):**
- ✅ Mínimo: **30 fps** em resolução máxima
- ✅ Configurável: Até 60 fps (se necessário)

**Compressão de Vídeo:**
- ✅ Padrões: **H.265 (HEVC), H.264, MJPEG**
- ✅ Múltiplos streams simultâneos (dual/triple stream)

**Recursos Avançados:**
- ✅ WDR (Wide Dynamic Range): ≥ 120 dB
- ✅ Visão noturna: IR até 30m mínimo
- ✅ 3D DNR (Redução de ruído digital)
- ✅ BLC/HLC (Compensação de contraluz)
- ✅ Defog (Desembaçamento digital)

**Proteção:**
- ✅ Grau de proteção: **IP67** ou superior (uso externo)
- ✅ Vandalismo: IK10 (se aplicável)
- ✅ Temperatura operacional: -30°C a +60°C (uso externo)

**Conectividade:**
- ✅ Interface: **RJ-45 10/100/1000 Mbps (Gigabit Ethernet)**
- ✅ PoE: IEEE 802.3af ou 802.3at
- ✅ Protocolos: ONVIF Profile S, G, T (interoperabilidade)

**Armazenamento Local (opcional):**
- ✅ Slot micro SD/SDHC/SDXC
- ✅ Capacidade: Até 256 GB ou superior
- ✅ Gravação em caso de falha de rede (failover)

**Exemplo de Especificação:**
```
Câmera IP externa tipo bullet com as seguintes características mínimas:
- Resolução: 4 MP (2688x1520) real
- Sensor: CMOS 1/2.8" progressivo
- Lente: Varifocal motorizada 2.8-12mm, F/1.4
- FPS: 30 fps @ 4MP
- Compressão: H.265/H.264/MJPEG, triple stream
- WDR: Mínimo 120 dB
- IR: Alcance mínimo 30 metros
- Proteção: IP67, IK10
- PoE: IEEE 802.3at
- Protocolos: ONVIF Profile S, compatível com VMS padrão
- Temperatura: -30°C a +60°C
```

### 2.2 Servidores / Estações de Trabalho

**Processador:**
- ✅ Arquitetura: x86-64 bits
- ✅ Núcleos: Mínimo 4 cores / 8 threads
- ✅ Frequência: ≥ 2.5 GHz (base)
- ✅ Desempenho: Benchmark PassMark ≥ 10.000 pontos (verificável)

**Memória RAM:**
- ✅ Tipo: DDR4 ou DDR5
- ✅ Capacidade mínima: **16 GB**
- ✅ Expansível até: 64 GB ou superior
- ✅ Velocidade: ≥ 2666 MHz

**Armazenamento:**
- ✅ Primário: SSD NVMe ≥ 500 GB
- ✅ Secundário: HDD SATA ≥ 2 TB (se necessário)
- ✅ RAID: Controladora RAID 1 ou 5 (para servidores críticos)

**Placa-Mãe:**
- ✅ Slots PCIe: Mínimo 2x PCIe 3.0 x16
- ✅ Portas USB: Mínimo 4x USB 3.0
- ✅ Interfaces de rede: 2x Gigabit Ethernet (redundância)

**Placa de Vídeo (se aplicável):**
- ✅ Memória dedicada: ≥ 4 GB GDDR6
- ✅ Suporte: DirectX 12, OpenGL 4.6
- ✅ Saídas: HDMI 2.0, DisplayPort 1.4

**Fonte de Alimentação:**
- ✅ Potência: ≥ 500W
- ✅ Certificação: 80 Plus Bronze ou superior
- ✅ Redundância: Fonte dupla (para servidores críticos)

**Conectividade:**
- ✅ Rede: 2x Gigabit Ethernet RJ-45
- ✅ USB: 6x USB 3.0 (mínimo)
- ✅ Áudio: Entrada/saída padrão

**Sistema de Refrigeração:**
- ✅ Dissipação adequada para operação 24x7
- ✅ Ruído: < 40 dB (ambientes office)

**Garantia:**
- ✅ Mínimo: **3 anos on-site**
- ✅ SLA: Atendimento em até 24 horas úteis

### 2.3 Storages / NAS / NVR

**Capacidade:**
- ✅ Calculada com base em:
  - Número de câmeras
  - Resolução e FPS
  - Taxa de compressão
  - Período de retenção (ex: 30, 60, 90 dias)
- ✅ Exemplo: 100 câmeras 4MP @ 15fps, H.265, 60 dias ≈ 150 TB

**Performance:**
- ✅ Taxa de gravação: ≥ 400 Mbps agregado
- ✅ Taxa de reprodução: ≥ 200 Mbps simultâneo
- ✅ Suporte: Mínimo 64 canais de vídeo (ou conforme necessidade)

**Discos Rígidos:**
- ✅ Tipo: **Enterprise** ou **Surveillance-rated** (WD Purple, Seagate SkyHawk)
- ✅ Capacidade individual: 6 TB a 12 TB
- ✅ RPM: 7200 rpm
- ✅ Cache: ≥ 256 MB
- ✅ MTBF: ≥ 1.000.000 horas
- ✅ Garantia: Mínimo 3 anos

**RAID:**
- ✅ Níveis suportados: RAID 0, 1, 5, 6, 10
- ✅ Recomendado: RAID 5 ou RAID 6 (redundância)
- ✅ Hot-swap: Troca a quente de discos

**Conectividade:**
- ✅ Rede: 2x Gigabit Ethernet (link aggregation)
- ✅ Portas: USB 3.0 (backup externo)
- ✅ eSATA (opcional)

**Protocolos de Rede:**
- ✅ SMB/CIFS, NFS, FTP, iSCSI
- ✅ ONVIF (para NVR)

**Redundância:**
- ✅ Fonte de alimentação: Dupla redundante
- ✅ Ventilação: Múltiplos ventiladores

**Backup:**
- ✅ Agendamento automático
- ✅ Snapshots
- ✅ Replicação para storage secundário

### 2.4 Switches de Rede

**Portas:**
- ✅ Quantidade: Conforme necessidade (ex: 24, 48 portas)
- ✅ Tipo: Gigabit Ethernet (10/100/1000 Mbps)
- ✅ Uplink: 2x SFP+ 10 Gbps (mínimo para switches de distribuição)

**PoE (Power over Ethernet):**
- ✅ Padrão: IEEE 802.3af (PoE) e 802.3at (PoE+)
- ✅ Budget total: ≥ 370W (para switch 24 portas PoE)
- ✅ Por porta: 30W (PoE+)

**Gerenciamento:**
- ✅ Tipo: **Gerenciável** (Layer 2 ou Layer 3)
- ✅ Interface: Web, CLI, SNMP v2/v3
- ✅ VLAN: Suporte a 802.1Q (mínimo 256 VLANs)
- ✅ QoS: IEEE 802.1p, DiffServ

**Segurança:**
- ✅ Autenticação: 802.1X (port-based)
- ✅ ACL (Access Control Lists)
- ✅ DHCP Snooping, IP Source Guard
- ✅ Storm Control

**Redundância:**
- ✅ Protocolo: STP, RSTP, MSTP
- ✅ Link aggregation: IEEE 802.3ad (LACP)

**Performance:**
- ✅ Backplane: Não bloqueante (wire-speed)
- ✅ Throughput: Line rate em todas as portas
- ✅ Latência: < 10 µs

**Montagem:**
- ✅ Rack: 19" padrão
- ✅ Altura: 1U ou 2U

**Garantia:**
- ✅ Lifetime ou mínimo 5 anos

---

## 3. Requisitos de Software

### 3.1 VMS (Video Management System)

**Funcionalidades Essenciais:**

✅ **Gravação:**
- Gravação contínua, agendada, por evento
- Configuração individual por câmera
- Pré e pós-alarme

✅ **Visualização:**
- Visualização ao vivo de múltiplas câmeras (grid configurável)
- Reprodução de gravações
- Zoom digital
- PTZ control (se aplicável)

✅ **Busca:**
- Por data/hora
- Por evento
- Por movimento (motion detection)
- Por metadados (analíticos)

✅ **Alertas:**
- Detecção de movimento
- Perda de vídeo
- Falha de gravação
- Notificações (e-mail, SMS, push)

✅ **Analíticos:**
- Detecção de movimento avançada
- Crossing line, intrusion detection
- Contagem de pessoas
- Reconhecimento facial (se aplicável)
- LPR - Leitura de Placas (se aplicável)

✅ **Administração:**
- Gestão de usuários e permissões (RBAC)
- Logs de auditoria
- Backup e exportação de vídeos
- Configuração centralizada

**Arquitetura:**
- ✅ Cliente-servidor ou web-based
- ✅ Multi-servidor (arquitetura distribuída para escalabilidade)
- ✅ Fail-over e redundância

**Compatibilidade:**
- ✅ Protocolo: **ONVIF** (interoperabilidade)
- ✅ Suporte: Mínimo 100 fabricantes de câmeras diferentes
- ✅ Plataforma: Windows Server e/ou Linux

**Licenciamento:**
- ✅ Modelo: Por canal/câmera ou por servidor
- ✅ Upgrades: Incluídos por X anos
- ✅ Suporte técnico: Incluído

**Performance:**
- ✅ Suporte: Mínimo 500 câmeras por servidor (ou conforme necessidade)
- ✅ Latência de visualização: < 500 ms

**Segurança:**
- ✅ Autenticação: LDAP/Active Directory
- ✅ Comunicação: HTTPS, TLS 1.2+
- ✅ Criptografia de vídeo: AES-256 (opcional)

**Exemplo de Especificação:**
```
VMS com as seguintes características:
- Suporte mínimo: 200 câmeras IP
- Protocolos: ONVIF, RTSP, HTTP
- Compatibilidade: Mínimo 50 fabricantes
- Gravação: Contínua, agendada, por evento
- Analíticos: Motion detection, line crossing, intrusion
- Interface: Cliente Windows e Web
- Licenciamento: Perpétuo com 3 anos de suporte
- Segurança: Integração com Active Directory, HTTPS
```

### 3.2 Sistemas Operacionais

**Servidores:**
- ✅ Windows Server 2019/2022 Standard ou Datacenter
- ✅ Ou: Linux (Ubuntu Server LTS, Red Hat Enterprise, CentOS)
- ✅ Licenciamento: Incluído ou especificado separadamente

**Estações de Trabalho:**
- ✅ Windows 10/11 Pro (64 bits)
- ✅ Licenciamento: OEM ou Volume

**Atualizações:**
- ✅ Suporte a atualizações de segurança por mínimo 5 anos

### 3.3 Banco de Dados

**Para Aplicações:**
- ✅ PostgreSQL 12+ (open-source)
- ✅ MySQL 8+ (open-source)
- ✅ Microsoft SQL Server 2019+ (comercial)
- ✅ Oracle Database (para grandes volumes)

**Características:**
- ✅ Transacional (ACID)
- ✅ Backup automatizado
- ✅ Replicação (alta disponibilidade)

### 3.4 Antivírus e Segurança

**Proteção de Endpoints:**
- ✅ Antivírus corporativo
- ✅ Firewall integrado
- ✅ Anti-malware, anti-ransomware
- ✅ Gerenciamento centralizado
- ✅ Atualizações automáticas

**Exemplos de Soluções:**
- Kaspersky Endpoint Security
- Symantec Endpoint Protection
- Trend Micro
- McAfee ou equivalente técnico

---

## 4. Requisitos de Rede e Conectividade

### 4.1 Topologia de Rede

**Recomendações:**
- ✅ Arquitetura: Estrela estendida
- ✅ Camadas: Acesso → Distribuição → Core
- ✅ Redundância: Links duplos entre camadas críticas

**Exemplo para 100 Câmeras:**
```
[Core Switch - Layer 3]
       ↓  ↓  (2x 10G uplinks)
[Distribution Switches - Layer 2] (2 unidades)
       ↓  ↓  ↓  (Gigabit downlinks)
[Access Switches PoE] (4 unidades, 24 portas cada)
       ↓  ↓  ↓  ↓
   [Câmeras IP]
```

### 4.2 Largura de Banda

**Cálculo:**
```
Bitrate por Câmera (H.265, 4MP, 15 fps) ≈ 2-4 Mbps
100 câmeras × 3 Mbps = 300 Mbps

Considerar:
+ 30% overhead ≈ 390 Mbps
+ Visualização ao vivo (clientes) ≈ +50 Mbps
= ~450 Mbps de backbone necessário
```

**Recomendação:**
- ✅ Backbone: **10 Gbps** (Core ↔ Distribuição)
- ✅ Distribuição ↔ Acesso: Gigabit agregado (LACP)
- ✅ Acesso ↔ Câmeras: Gigabit por porta

### 4.3 Endereçamento IP

**Sugestão de Segmentação:**
```
VLAN 10 - Gerenciamento: 192.168.10.0/24
VLAN 20 - Câmeras: 10.20.0.0/16 (até 65k câmeras)
VLAN 30 - Storages: 10.30.0.0/24
VLAN 40 - Clientes/Operadores: 192.168.40.0/24
```

**DHCP:**
- ✅ Servidor DHCP para câmeras (facilita implantação)
- ✅ Reservas DHCP por MAC address (IPs fixos)
- ✅ Ou: IPs estáticos configurados manualmente

### 4.4 Qualidade de Serviço (QoS)

**Priorização de Tráfego:**
```
Prioridade 1 (Mais alta): Vídeo ao vivo
Prioridade 2: Gravação
Prioridade 3: Gerenciamento (SNMP, SSH)
Prioridade 4: Dados gerais
```

**Implementação:**
- ✅ 802.1p (CoS - Layer 2)
- ✅ DiffServ (DSCP - Layer 3)

### 4.5 Cabeamento

**Cabeamento Estruturado:**
- ✅ Padrão: **Cat6 ou Cat6A** (suporta até 10 Gbps)
- ✅ Comprimento máximo: 100 metros (UTP)
- ✅ Conectorização: RJ-45 certificada
- ✅ Certificação: Testes de performance (Fluke ou similar)

**Proteção:**
- ✅ Eletrodutos metálicos ou PVC rígido
- ✅ Aterramento adequado
- ✅ DPS (Dispositivo de Proteção contra Surtos) nas câmeras externas

---

## 5. Requisitos de Segurança

### 5.1 Segurança Física

**Equipamentos:**
- ✅ Racks: Fechados com chave, ventilação adequada
- ✅ Câmeras: Anti-vandalismo (IK10) em áreas públicas
- ✅ Acesso: Restrito a pessoal autorizado

**Ambiente:**
- ✅ Sala de equipamentos: Controle de acesso
- ✅ Refrigeração: Ar-condicionado 24x7
- ✅ No-break: Autonomia mínima 30 minutos

### 5.2 Segurança Lógica

**Autenticação:**
- ✅ Usuários e senhas fortes (mínimo 12 caracteres)
- ✅ Autenticação de dois fatores (2FA) - recomendado
- ✅ Integração com Active Directory/LDAP

**Autorização:**
- ✅ RBAC (Role-Based Access Control)
- ✅ Princípio do menor privilégio
- ✅ Logs de auditoria (quem acessou o quê, quando)

**Comunicação:**
- ✅ HTTPS para interfaces web
- ✅ TLS 1.2 ou superior
- ✅ Certificados SSL válidos

**Criptografia:**
- ✅ Vídeos sensíveis: AES-256
- ✅ Banco de dados: Criptografia em repouso
- ✅ Comunicação: Criptografia em trânsito

**Firewall:**
- ✅ Segmentação de rede (VLANs)
- ✅ Firewall entre VLANs críticas
- ✅ ACLs nos switches

**Atualizações:**
- ✅ Firmware de câmeras: Atualizado regularmente
- ✅ SO e software: Patches de segurança aplicados
- ✅ Antivírus: Definições atualizadas

### 5.3 Conformidade

**LGPD (Lei Geral de Proteção de Dados):**
- ✅ Política de privacidade
- ✅ Tempo de retenção definido e justificado
- ✅ Acesso controlado e auditado
- ✅ Exclusão segura ao final da retenção

**Normas Técnicas:**
- ✅ ABNT NBR ISO/IEC 27001 (Gestão de Segurança da Informação)
- ✅ ABNT NBR IEC 62676 (Sistemas CFTV)

---

## 6. Requisitos de Integração

### 6.1 Protocolos e APIs

**Padrões Abertos:**
- ✅ **ONVIF** (Open Network Video Interface Forum)
  - Profile S: Streaming
  - Profile G: Gravação
  - Profile T: Analíticos avançados

- ✅ **RTSP** (Real-Time Streaming Protocol)
- ✅ **HTTP/HTTPS** (APIs RESTful)

**APIs:**
- ✅ API RESTful documentada
- ✅ Webhooks para eventos
- ✅ SDK (Software Development Kit) disponível

**Formato de Dados:**
- ✅ JSON, XML
- ✅ Protobuf (para alta performance)

### 6.2 Integração com Sistemas Terceiros

**Controle de Acesso:**
- ✅ Integração com sistemas de catracas, fechaduras eletrônicas
- ✅ Correlação de eventos (porta aberta → disparo de câmera)

**Alarmes:**
- ✅ Integração com central de alarmes
- ✅ Disparo de gravação em eventos de alarme

**ERP/CRM:**
- ✅ Exportação de relatórios (CSV, Excel, PDF)
- ✅ Integração via API para automação

**Exemplo:**
```
O VMS deve possuir API RESTful documentada, permitindo integração com sistemas
de controle de acesso (ex: disparo de gravação ao detectar porta aberta) e
exportação de eventos em formato JSON para análise externa.
```

---

## 7. Requisitos de Desempenho

### 7.1 Disponibilidade

**Uptime:**
- ✅ SLA: **99,5%** (padrão)
- ✅ SLA: **99,9%** (alta disponibilidade) - ~8h downtime/ano
- ✅ SLA: **99,99%** (missão crítica) - ~52min downtime/ano

**Componentes para Alta Disponibilidade:**
- ✅ Servidores redundantes (failover)
- ✅ Storages com RAID
- ✅ Fontes de alimentação redundantes
- ✅ Links de rede redundantes
- ✅ No-breaks com autonomia adequada

### 7.2 Escalabilidade

**Horizontal:**
- ✅ Adição de novos servidores conforme crescimento
- ✅ Arquitetura distribuída

**Vertical:**
- ✅ Upgrade de hardware (CPU, RAM, storage)

**Exemplo:**
```
O sistema deve suportar expansão de 100 para 500 câmeras mediante adição de
servidores de gravação e storage, sem necessidade de substituição da plataforma.
```

### 7.3 Performance

**Latência:**
- ✅ Visualização ao vivo: < 500 ms
- ✅ Resposta de busca: < 3 segundos para query de 30 dias

**Throughput:**
- ✅ Gravação simultânea de 100% das câmeras em resolução máxima

**Concorrência:**
- ✅ Mínimo 10 operadores simultâneos visualizando ao vivo

---

## 8. Requisitos de Suporte e Manutenção

### 8.1 Garantia

**Equipamentos:**
- ✅ Mínimo: **3 anos on-site**
- ✅ Atendimento: 8x5 (horário comercial) ou 24x7 (crítico)
- ✅ SLA de atendimento: 24 horas úteis (8x5) ou 4 horas (24x7)
- ✅ SLA de resolução: Conforme criticidade

**Software:**
- ✅ Atualizações de versão: Incluídas por X anos
- ✅ Patches de segurança: Vitalícios
- ✅ Suporte técnico: Telefone, e-mail, chat

### 8.2 Treinamento

**Operação:**
- ✅ Mínimo: **40 horas** de treinamento para operadores
- ✅ Conteúdo: Visualização, busca, exportação, alarmes

**Administração:**
- ✅ Mínimo: **24 horas** de treinamento para administradores
- ✅ Conteúdo: Configuração, usuários, backup, troubleshooting

**Material:**
- ✅ Manuais em português
- ✅ Vídeos tutoriais
- ✅ Certificados de conclusão

### 8.3 Documentação

**Técnica:**
- ✅ Manual de instalação
- ✅ Manual de configuração
- ✅ Diagramas de rede (as-built)
- ✅ Planilha de endereçamento IP
- ✅ Credenciais de acesso (em envelope lacrado)

**Usuário:**
- ✅ Manual de operação
- ✅ Guia de troubleshooting
- ✅ FAQ

**Formato:**
- ✅ Português do Brasil
- ✅ PDF e/ou impresso

---

## 9. Certificações e Conformidades

### 9.1 Certificações de Produto

**Segurança Elétrica:**
- ✅ **INMETRO** (produtos nacionais)
- ✅ **ANATEL** (equipamentos de telecomunicação)
- ✅ CE, FCC (produtos importados)

**Qualidade:**
- ✅ ISO 9001 (Fabricante)

**Ambiental:**
- ✅ RoHS (Restriction of Hazardous Substances)
- ✅ WEEE (Waste Electrical and Electronic Equipment)

### 9.2 Certificações de Empresa

**Fornecedor:**
- ✅ Registro na Junta Comercial
- ✅ Regularidade fiscal
- ✅ Certificações ISO (desejável): ISO 9001, ISO 27001

**Instalador:**
- ✅ Técnico responsável com registro profissional (CREA)
- ✅ Certificação do fabricante (se aplicável)
- ✅ ART (Anotação de Responsabilidade Técnica)

### 9.3 Normas Técnicas Aplicáveis

**Sistemas de CFTV:**
- ✅ ABNT NBR IEC 62676-1-1 (Parte 1: Requisitos do sistema)
- ✅ ABNT NBR IEC 62676-1-2 (Parte 2: Especificações humanas)
- ✅ ABNT NBR IEC 62676-2-1 (Parte 2-1: Câmeras analogicas e digitais)
- ✅ ABNT NBR IEC 62676-4 (Parte 4: Diretrizes de aplicação)

**Cabeamento:**
- ✅ ABNT NBR 14565 (Cabeamento estruturado)
- ✅ TIA/EIA-568 (Cabeamento comercial)

**Segurança da Informação:**
- ✅ ABNT NBR ISO/IEC 27001 (SGSI)
- ✅ ABNT NBR ISO/IEC 27002 (Controles)

**Proteção:**
- ✅ IEC 60529 (Graus de proteção IP)
- ✅ IEC 62262 (Graus de proteção IK)

---

## 10. Exemplos Práticos por Categoria

### 10.1 Sistema de CFTV - 100 Câmeras

**Resumo de Requisitos:**

```
CÂMERAS: 100 unidades
- Tipo: 80 bullet (externa), 20 dome (interna)
- Resolução: 4 MP (2688x1520)
- FPS: 30 fps @ 4MP
- Compressão: H.265
- IR: 30m (externas), 20m (internas)
- PoE: IEEE 802.3at
- Proteção: IP67 / IK10 (externas), IP42 (internas)
- Protocolo: ONVIF Profile S

REDE:
- Switches acesso: 5x 24 portas PoE+ (370W)
- Switches distribuição: 2x 48 portas + 4x SFP+ 10G
- Cabeamento: Cat6 certificado

STORAGE:
- Tipo: NVR ou servidor + storage NAS
- Capacidade: 150 TB (60 dias retenção)
- RAID: RAID 6
- Discos: 12x 14 TB surveillance-rated

VMS:
- Licenças: 100 canais
- Protocolo: ONVIF
- Interface: Cliente Windows + Web
- Analíticos: Motion, line crossing, intrusion

SERVIDORES:
- 2x servidores (gravação redundante)
- CPU: 8 cores, 3 GHz
- RAM: 32 GB
- SSD: 500 GB (SO + aplicações)

NO-BREAK:
- Potência: 5 kVA
- Autonomia: 30 minutos (full load)

GARANTIA:
- Equipamentos: 3 anos on-site
- Software: 3 anos de suporte e atualizações

TREINAMENTO:
- Operação: 40 horas (10 operadores)
- Administração: 24 horas (3 admins)
```

### 10.2 Controle de Acesso - 50 Pontos

```
CONTROLADORES:
- 10 controladores de acesso (5 portas cada)
- Protocolo: Wiegand 26/34, TCP/IP
- Capacidade: 100.000 usuários
- Offline: Funciona sem servidor

LEITORES:
- 50 leitores RFID 125 kHz ou 13,56 MHz
- Tipo: Proximidade ou biométrico (impressão digital)
- Proteção: IP65 (externos), IP42 (internos)

FECHADURAS:
- 50 fechaduras eletromagnéticas (150 kgf) ou eletroimãs

SOFTWARE:
- Licença: 50 portas + 100.000 usuários
- Interface: Web-based
- Integração: API RESTful, webhook events
- Relatórios: Exportação CSV, PDF

REDE:
- Switch gerenciável 48 portas
- Cabeamento Cat6

SERVIDOR:
- CPU: 4 cores
- RAM: 16 GB
- SSD: 250 GB

BACKUP:
- Retenção de logs: 5 anos
- Backup automático diário
```

### 10.3 Sistema de Alarme - Edifício Comercial

```
CENTRAL DE ALARME:
- Zonas: 64 mistas (cabeadas + sem fio)
- Comunicação: Ethernet, Wi-Fi, 4G (backup)
- Bateria: 12V 7Ah (autonomia 24h)

SENSORES:
- 40 sensores de presença infravermelho passivo
- 20 sensores magnéticos (portas/janelas)
- 10 detectores de quebra de vidro
- Proteção: Anti-mascaramento, anti-sabotagem

SIRENES:
- 8 sirenes piezoeléctricas (internas)
- 4 sirenes com flash (externas, IP65)

SOFTWARE:
- Monitoramento remoto (app mobile)
- Notificações push, e-mail, SMS
- Histórico de eventos: 6 meses
- Integração com CFTV (disparo de gravação)

INSTALAÇÃO:
- Cabeamento dedicado
- Aterramento adequado
- Baterias de backup
```

---

## 11. Checklist de Validação de Requisitos

Antes de publicar o edital, verificar:

✅ **Especificações Técnicas:**
- [ ] Todos os requisitos são mensuráveis?
- [ ] Há referência a normas técnicas reconhecidas?
- [ ] Evitou-se citar marcas ou modelos específicos?
- [ ] Adicionou-se "ou equivalente técnico"?

✅ **Completude:**
- [ ] Todos os componentes necessários estão listados?
- [ ] Quantidades estão corretas?
- [ ] Acessórios e cabos incluídos?

✅ **Integração:**
- [ ] Compatibilidade entre componentes está garantida?
- [ ] Protocolos abertos (ONVIF, etc.) especificados?

✅ **Documentação:**
- [ ] Manuais em português exigidos?
- [ ] Treinamento especificado?
- [ ] Garantia e suporte definidos claramente?

✅ **Conformidade:**
- [ ] Certificações necessárias listadas (INMETRO, ANATEL)?
- [ ] Normas técnicas referenciadas?

✅ **Performance:**
- [ ] Requisitos de disponibilidade especificados?
- [ ] Escalabilidade prevista?
- [ ] Testes de aceitação definidos?

---

**Última Atualização:** Novembro de 2025
**Fonte:** Normas ABNT, boas práticas de mercado, TCU
**Aplicação:** Editais de licitação para sistemas de TI, segurança e infraestrutura
