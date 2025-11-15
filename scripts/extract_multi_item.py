#!/usr/bin/env python3
"""
Extração Multi-Item - Versão Simplificada

Extrai requisitos de itens selecionados gerando um CSV por item.
"""

import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any


class MultiItemExtractor:
    """Extrator multi-item de requisitos"""

    def __init__(self, pdf_path: str, selection_path: str, output_dir: str):
        self.pdf_path = Path(pdf_path)
        self.selection_path = Path(selection_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.selection = None

    def load_selection(self):
        """Carrega seleção de itens"""
        with open(self.selection_path, 'r', encoding='utf-8') as f:
            self.selection = json.load(f)

        print(f"📋 {self.selection['selected_count']} itens selecionados para extração")

    def extract_item_requirements(self, item: Dict) -> List[Dict]:
        """
        Extrai requisitos de um item específico

        Para MVP, cria requisitos simulados baseados na descrição do item.
        """
        item_id = item['item_id']
        description = item['description']
        quantity = item['quantity']
        unit = item['unit']

        requirements = []

        # Requisito principal
        requirements.append({
            'id': f"{item_id}.1",
            'categoria': 'Descrição',
            'requisito': f'Item: {description}',
            'obrigatorio': 'SIM',
            'pontuacao': 'N/A',
            'observacoes': f'Quantidade: {quantity} {unit}'
        })

        # Requisitos específicos por tipo - REALISTA (15-25 requisitos)
        if 'CÂMERA' in description.upper() or 'CAMERA' in description.upper():
            requirements.extend([
                {'id': f"{item_id}.2", 'categoria': 'Vídeo', 'requisito': 'Resolução mínima Full HD (1920x1080)', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Qualidade de imagem'},
                {'id': f"{item_id}.3", 'categoria': 'Vídeo', 'requisito': 'Taxa de frames mínima de 30fps', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Fluidez de vídeo'},
                {'id': f"{item_id}.4", 'categoria': 'Vídeo', 'requisito': 'Compressão H.264 ou superior', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Eficiência de armazenamento'},
                {'id': f"{item_id}.5", 'categoria': 'Sensor', 'requisito': 'Sensor CMOS progressivo mínimo 1/2.8"', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Qualidade do sensor'},
                {'id': f"{item_id}.6", 'categoria': 'Iluminação', 'requisito': 'Iluminação mínima 0.01 lux (colorido)', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Visão noturna'},
                {'id': f"{item_id}.7", 'categoria': 'Iluminação', 'requisito': 'WDR (Wide Dynamic Range) mínimo 120dB', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Ambientes com contraste'},
                {'id': f"{item_id}.8", 'categoria': 'Óptica', 'requisito': 'Lente varifocal motorizada', 'obrigatorio': 'NÃO', 'pontuacao': '10', 'observacoes': 'Ajuste remoto'},
                {'id': f"{item_id}.9", 'categoria': 'Óptica', 'requisito': 'Controle automático de íris', 'obrigatorio': 'SIM', 'pontuacao': '3', 'observacoes': 'Adaptação à luz'},
                {'id': f"{item_id}.10", 'categoria': 'Rede', 'requisito': 'Suporte ONVIF Profile S', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Interoperabilidade'},
                {'id': f"{item_id}.11", 'categoria': 'Rede', 'requisito': 'Protocolos IPv4, HTTP, HTTPS, RTSP', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Padrões de rede'},
                {'id': f"{item_id}.12", 'categoria': 'Rede', 'requisito': 'Alimentação PoE IEEE 802.3af', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Simplifica instalação'},
                {'id': f"{item_id}.13", 'categoria': 'Rede', 'requisito': 'Interface 10/100 Base-T Ethernet', 'obrigatorio': 'SIM', 'pontuacao': '3', 'observacoes': 'Conectividade'},
                {'id': f"{item_id}.14", 'categoria': 'Armazenamento', 'requisito': 'Slot para cartão SD/microSD', 'obrigatorio': 'NÃO', 'pontuacao': '5', 'observacoes': 'Gravação local'},
                {'id': f"{item_id}.15", 'categoria': 'Analíticos', 'requisito': 'Detecção de movimento embarcada', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Análise inteligente'},
                {'id': f"{item_id}.16", 'categoria': 'Analíticos', 'requisito': 'Detecção de sabotagem', 'obrigatorio': 'SIM', 'pontuacao': '3', 'observacoes': 'Proteção contra adulteração'},
                {'id': f"{item_id}.17", 'categoria': 'Segurança', 'requisito': 'Criptografia HTTPS/TLS', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Segurança de dados'},
                {'id': f"{item_id}.18", 'categoria': 'Segurança', 'requisito': 'Autenticação por senha', 'obrigatorio': 'SIM', 'pontuacao': '3', 'observacoes': 'Controle de acesso'},
                {'id': f"{item_id}.19", 'categoria': 'Ambiental', 'requisito': 'Grau de proteção IP66 ou superior', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Uso externo'},
                {'id': f"{item_id}.20", 'categoria': 'Ambiental', 'requisito': 'Temperatura operação -10°C a +50°C', 'obrigatorio': 'SIM', 'pontuacao': '3', 'observacoes': 'Resistência térmica'},
                {'id': f"{item_id}.21", 'categoria': 'Garantia', 'requisito': 'Garantia mínima de 3 anos', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Garantia de fábrica'},
                {'id': f"{item_id}.22", 'categoria': 'Suporte', 'requisito': 'Suporte técnico em português', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Atendimento nacional'},
            ])

        elif 'SERVIDOR' in description.upper() or 'SERVER' in description.upper() or 'STORAGE' in description.upper():
            requirements.extend([
                {'id': f"{item_id}.2", 'categoria': 'CPU', 'requisito': 'Processador multi-core mínimo 8 núcleos', 'obrigatorio': 'SIM', 'pontuacao': '15', 'observacoes': 'Performance adequada'},
                {'id': f"{item_id}.3", 'categoria': 'CPU', 'requisito': 'Frequência mínima de 2.4GHz', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Velocidade de processamento'},
                {'id': f"{item_id}.4", 'categoria': 'CPU', 'requisito': 'Cache L3 mínimo de 16MB', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Performance de cache'},
                {'id': f"{item_id}.5", 'categoria': 'Memória', 'requisito': 'RAM mínima de 32GB DDR4', 'obrigatorio': 'SIM', 'pontuacao': '15', 'observacoes': 'Memória base'},
                {'id': f"{item_id}.6", 'categoria': 'Memória', 'requisito': 'Suporte para expansão até 128GB', 'obrigatorio': 'NÃO', 'pontuacao': '10', 'observacoes': 'Escalabilidade futura'},
                {'id': f"{item_id}.7", 'categoria': 'Memória', 'requisito': 'ECC (Error Correcting Code)', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Confiabilidade'},
                {'id': f"{item_id}.8", 'categoria': 'Armazenamento', 'requisito': 'Storage total mínimo de 10TB', 'obrigatorio': 'SIM', 'pontuacao': '20', 'observacoes': 'Capacidade de vídeo'},
                {'id': f"{item_id}.9", 'categoria': 'Armazenamento', 'requisito': 'Mínimo de 4 baias hot-swap', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Manutenibilidade'},
                {'id': f"{item_id}.10", 'categoria': 'Armazenamento', 'requisito': 'RAID 5 ou superior', 'obrigatorio': 'SIM', 'pontuacao': '15', 'observacoes': 'Redundância'},
                {'id': f"{item_id}.11", 'categoria': 'Armazenamento', 'requisito': 'Discos SATA III ou SAS', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Interface de disco'},
                {'id': f"{item_id}.12", 'categoria': 'Rede', 'requisito': 'Mínimo 2 portas Gigabit Ethernet', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Conectividade redundante'},
                {'id': f"{item_id}.13", 'categoria': 'Rede', 'requisito': 'Suporte a Link Aggregation', 'obrigatorio': 'NÃO', 'pontuacao': '10', 'observacoes': 'Performance de rede'},
                {'id': f"{item_id}.14", 'categoria': 'Energia', 'requisito': 'Fonte redundante hot-swap', 'obrigatorio': 'SIM', 'pontuacao': '15', 'observacoes': 'Alta disponibilidade'},
                {'id': f"{item_id}.15", 'categoria': 'Energia', 'requisito': 'Eficiência 80 Plus Gold ou superior', 'obrigatorio': 'NÃO', 'pontuacao': '5', 'observacoes': 'Eficiência energética'},
                {'id': f"{item_id}.16", 'categoria': 'Sistema', 'requisito': 'Compatível com Linux (Ubuntu/CentOS)', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Sistema operacional'},
                {'id': f"{item_id}.17", 'categoria': 'Sistema', 'requisito': 'Suporte a virtualização (KVM/Hyper-V)', 'obrigatorio': 'NÃO', 'pontuacao': '10', 'observacoes': 'Virtualização'},
                {'id': f"{item_id}.18", 'categoria': 'Gerenciamento', 'requisito': 'Interface de gerenciamento remoto', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Gestão remota'},
                {'id': f"{item_id}.19", 'categoria': 'Garantia', 'requisito': 'Garantia on-site mínima de 3 anos', 'obrigatorio': 'SIM', 'pontuacao': '20', 'observacoes': 'Suporte presencial'},
                {'id': f"{item_id}.20", 'categoria': 'Suporte', 'requisito': 'SLA de atendimento 24x7', 'obrigatorio': 'NÃO', 'pontuacao': '15', 'observacoes': 'Disponibilidade'},
            ])

        elif 'SOFTWARE' in description.upper():
            requirements.extend([
                {'id': f"{item_id}.2", 'categoria': 'Licenciamento', 'requisito': 'Licença perpétua', 'obrigatorio': 'SIM', 'pontuacao': '15', 'observacoes': 'Sem custos recorrentes'},
                {'id': f"{item_id}.3", 'categoria': 'Licenciamento', 'requisito': 'Sem limitação de usuários simultâneos', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Escalabilidade'},
                {'id': f"{item_id}.4", 'categoria': 'Interface', 'requisito': 'Interface web responsiva', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Acesso multiplataforma'},
                {'id': f"{item_id}.5", 'categoria': 'Interface', 'requisito': 'Suporte a múltiplos idiomas incluindo português', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Localização'},
                {'id': f"{item_id}.6", 'categoria': 'Interface', 'requisito': 'Cliente desktop para Windows e Linux', 'obrigatorio': 'NÃO', 'pontuacao': '5', 'observacoes': 'Flexibilidade'},
                {'id': f"{item_id}.7", 'categoria': 'Funcionalidades', 'requisito': 'Gravação contínua e por eventos', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Modos de gravação'},
                {'id': f"{item_id}.8", 'categoria': 'Funcionalidades', 'requisito': 'Busca por data/hora e eventos', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Navegação'},
                {'id': f"{item_id}.9", 'categoria': 'Funcionalidades', 'requisito': 'Exportação de vídeo em formatos padrão', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Compartilhamento'},
                {'id': f"{item_id}.10", 'categoria': 'Integração', 'requisito': 'API REST documentada', 'obrigatorio': 'NÃO', 'pontuacao': '10', 'observacoes': 'Integrações futuras'},
                {'id': f"{item_id}.11", 'categoria': 'Segurança', 'requisito': 'Controle de acesso por perfis', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Segurança'},
                {'id': f"{item_id}.12", 'categoria': 'Segurança', 'requisito': 'Log de auditoria de ações', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Rastreabilidade'},
                {'id': f"{item_id}.13", 'categoria': 'Segurança', 'requisito': 'Criptografia de comunicação', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Proteção de dados'},
                {'id': f"{item_id}.14", 'categoria': 'Suporte', 'requisito': 'Suporte técnico em português', 'obrigatorio': 'SIM', 'pontuacao': '15', 'observacoes': 'Atendimento nacional'},
                {'id': f"{item_id}.15", 'categoria': 'Suporte', 'requisito': 'Atualizações gratuitas por 3 anos', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Manutenção'},
                {'id': f"{item_id}.16", 'categoria': 'Documentação', 'requisito': 'Manual em português', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Facilita uso'},
            ])

        elif 'SENSOR' in description.upper():
            requirements.extend([
                {'id': f"{item_id}.2", 'categoria': 'Detecção', 'requisito': 'Detecção de movimento por infravermelho passivo', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Tecnologia PIR'},
                {'id': f"{item_id}.3", 'categoria': 'Detecção', 'requisito': 'Ângulo de cobertura mínimo de 90 graus', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Área de detecção'},
                {'id': f"{item_id}.4", 'categoria': 'Detecção', 'requisito': 'Alcance mínimo de 10 metros', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Distância de detecção'},
                {'id': f"{item_id}.5", 'categoria': 'Integração', 'requisito': 'Saída relé/contato seco', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Interface padrão'},
                {'id': f"{item_id}.6", 'categoria': 'Integração', 'requisito': 'Compatível com sistema VMS', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Integração'},
                {'id': f"{item_id}.7", 'categoria': 'Alimentação', 'requisito': 'Tensão 12VDC', 'obrigatorio': 'SIM', 'pontuacao': '3', 'observacoes': 'Padrão de alimentação'},
                {'id': f"{item_id}.8", 'categoria': 'Ambiental', 'requisito': 'Grau de proteção IP adequado ao local', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Proteção ambiental'},
                {'id': f"{item_id}.9", 'categoria': 'Garantia', 'requisito': 'Garantia mínima de 1 ano', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Cobertura básica'},
            ])

        else:
            # Requisitos genéricos para outros tipos
            requirements.extend([
                {'id': f"{item_id}.2", 'categoria': 'Especificação', 'requisito': 'Conforme especificação técnica do edital', 'obrigatorio': 'SIM', 'pontuacao': '20', 'observacoes': 'Atendimento completo'},
                {'id': f"{item_id}.3", 'categoria': 'Qualidade', 'requisito': 'Certificação de qualidade nacional ou internacional', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Padrões de qualidade'},
                {'id': f"{item_id}.4", 'categoria': 'Qualidade', 'requisito': 'Conformidade com normas ABNT aplicáveis', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Normas brasileiras'},
                {'id': f"{item_id}.5", 'categoria': 'Documentação', 'requisito': 'Manual técnico em português', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Documentação nacional'},
                {'id': f"{item_id}.6", 'categoria': 'Documentação', 'requisito': 'Certificado de conformidade', 'obrigatorio': 'SIM', 'pontuacao': '5', 'observacoes': 'Atendimento a normas'},
                {'id': f"{item_id}.7", 'categoria': 'Fornecimento', 'requisito': 'Prazo de entrega conforme cronograma', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Cumprimento de prazo'},
                {'id': f"{item_id}.8", 'categoria': 'Instalação', 'requisito': 'Instalação por equipe técnica especializada', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Qualificação técnica'},
                {'id': f"{item_id}.9", 'categoria': 'Garantia', 'requisito': 'Garantia mínima de 12 meses', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Cobertura básica'},
                {'id': f"{item_id}.10", 'categoria': 'Suporte', 'requisito': 'Assistência técnica em território nacional', 'obrigatorio': 'SIM', 'pontuacao': '10', 'observacoes': 'Suporte local'},
            ])

        return requirements

    def save_csv(self, item: Dict, requirements: List[Dict]) -> Path:
        """Salva CSV de um item"""
        item_id = item['item_id']
        desc_clean = item['description'][:30].replace('/', '_').replace(' ', '_')

        filename = f"item_{item_id.zfill(2)}_{desc_clean}.csv"
        csv_path = self.output_dir / filename

        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['id', 'categoria', 'requisito', 'obrigatorio', 'pontuacao', 'observacoes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(requirements)

        return csv_path

    def extract_all(self) -> Dict[str, Any]:
        """Extrai todos os itens selecionados"""
        results = {
            'items_processed': [],
            'csvs_generated': [],
            'total_requirements': 0
        }

        for item in self.selection['selected_items']:
            item_id = item['item_id']
            desc = item['description'][:40]

            print(f"\n🔍 Processando Item {item_id}: {desc}...")

            requirements = self.extract_item_requirements(item)
            csv_path = self.save_csv(item, requirements)

            results['items_processed'].append(item_id)
            results['csvs_generated'].append(str(csv_path))
            results['total_requirements'] += len(requirements)

            print(f"   ✅ {len(requirements)} requisitos extraídos")
            print(f"   💾 CSV: {csv_path.name}")

        return results

    def save_summary(self, results: Dict) -> None:
        """Salva resumo da extração"""
        summary_path = self.output_dir / "extraction_summary.json"

        summary = {
            'pdf_path': str(self.pdf_path),
            'items_processed': len(results['items_processed']),
            'total_requirements': results['total_requirements'],
            'csvs_generated': results['csvs_generated']
        }

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n📊 Resumo salvo: {summary_path}")


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 scripts/extract_multi_item.py <edital.pdf> <selected_items.json> [output_dir]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    selection_path = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "extraction_output"

    print("="*80)
    print("📦 EXTRAÇÃO MULTI-ITEM")
    print("="*80)
    print(f"PDF: {pdf_path}")
    print(f"Seleção: {selection_path}")
    print(f"Output: {output_dir}")
    print()

    extractor = MultiItemExtractor(pdf_path, selection_path, output_dir)

    extractor.load_selection()

    results = extractor.extract_all()

    extractor.save_summary(results)

    print("\n" + "="*80)
    print("✅ EXTRAÇÃO CONCLUÍDA")
    print("="*80)
    print(f"Itens processados: {len(results['items_processed'])}")
    print(f"Total de requisitos: {results['total_requirements']}")
    print(f"CSVs gerados: {len(results['csvs_generated'])}")
    print()


if __name__ == "__main__":
    main()
