# formatador_prova.py - Versão melhorada com formatação para impressão

from datetime import datetime

class ProvaENEM:
    def __init__(self):
        self.materia = "Química"
        self.tema = "Geral"
        self.nivel = "médio"
        self.resumo = ""
        self.questoes = []
        self.gabarito = []
        self.data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        
    def criar_prova(self, materia, tema, nivel):
        self.materia = materia
        self.tema = tema
        self.nivel = nivel
        
    def adicionar_questao(self, tipo, nivel, texto, alternativas=None, linhas=8):
        self.questoes.append({
            "numero": len(self.questoes) + 1,
            "tipo": tipo,
            "nivel": nivel,
            "texto": texto,
            "alternativas": alternativas or [],
            "espaco_linhas": linhas
        })
        
    def adicionar_ao_gabarito(self, numero, resposta, explicacao, erros_comuns=None):
        self.gabarito.append({
            "numero": numero,
            "resposta": resposta,
            "explicacao": explicacao,
            "erros_comuns": erros_comuns or []
        })
    
    def gerar_prova_aluno_html(self):
        """Gera HTML da prova para o aluno (formatado para impressão)"""
        
        niveis_icons = {
            "facil": "🟢",
            "medio": "🟡",
            "dificil": "🔴"
        }
        
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Prova - {self.materia} - {self.tema}</title>
            <style>
                @media print {{
                    body {{
                        margin: 0;
                        padding: 20px;
                    }}
                    .no-print {{
                        display: none;
                    }}
                    .page-break {{
                        page-break-before: always;
                    }}
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Times New Roman', 'Arial', serif;
                    background: white;
                    padding: 40px;
                    color: #1a1a1a;
                    font-size: 12pt;
                }}
                
                .prova-container {{
                    max-width: 1100px;
                    margin: 0 auto;
                    background: white;
                }}
                
                /* Cabeçalho da prova */
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 3px solid #2c3e50;
                }}
                
                .header h1 {{
                    font-size: 24pt;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                
                .header h2 {{
                    font-size: 16pt;
                    color: #34495e;
                    margin-bottom: 5px;
                }}
                
                .header .info {{
                    font-size: 11pt;
                    color: #7f8c8d;
                    margin-top: 10px;
                }}
                
                /* Informações do aluno */
                .student-info {{
                    background: #f8f9fa;
                    padding: 15px;
                    margin-bottom: 25px;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                }}
                
                .student-info table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                
                .student-info td {{
                    padding: 8px;
                    border-bottom: 1px solid #dee2e6;
                }}
                
                .student-info td:first-child {{
                    width: 120px;
                    font-weight: bold;
                    color: #2c3e50;
                }}
                
                /* Resumo rápido */
                .resumo {{
                    background: #e8f4f8;
                    padding: 15px;
                    margin-bottom: 25px;
                    border-left: 4px solid #3498db;
                    border-radius: 5px;
                }}
                
                .resumo h3 {{
                    color: #2980b9;
                    margin-bottom: 10px;
                    font-size: 14pt;
                }}
                
                .resumo p {{
                    line-height: 1.5;
                    text-align: justify;
                }}
                
                /* Questões */
                .questao {{
                    margin-bottom: 35px;
                    page-break-inside: avoid;
                }}
                
                .questao-header {{
                    margin-bottom: 12px;
                    padding: 8px 12px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    display: inline-block;
                }}
                
                .questao-numero {{
                    font-weight: bold;
                    font-size: 13pt;
                    color: #2c3e50;
                }}
                
                .questao-nivel {{
                    margin-left: 10px;
                    font-size: 10pt;
                    color: #7f8c8d;
                }}
                
                .questao-texto {{
                    margin-bottom: 15px;
                    line-height: 1.6;
                    text-align: justify;
                    font-size: 11pt;
                }}
                
                /* Alternativas múltipla escolha */
                .alternativas {{
                    margin: 15px 0;
                    padding-left: 20px;
                }}
                
                .alternativa {{
                    margin: 8px 0;
                    line-height: 1.5;
                }}
                
                .alternativa-letra {{
                    font-weight: bold;
                    display: inline-block;
                    width: 25px;
                    color: #2c3e50;
                }}
                
                /* Espaço para resposta */
                .espaco-resposta {{
                    margin-top: 15px;
                    padding: 10px;
                    border: 1px dashed #ccc;
                    background: #fefefe;
                }}
                
                .espaco-resposta h4 {{
                    font-size: 10pt;
                    color: #7f8c8d;
                    margin-bottom: 8px;
                }}
                
                .linhas-resposta {{
                    min-height: 150px;
                    border-top: 1px solid #ddd;
                    margin-top: 8px;
                }}
                
                /* Rodapé */
                .footer {{
                    margin-top: 40px;
                    padding-top: 15px;
                    border-top: 1px solid #dee2e6;
                    text-align: center;
                    font-size: 9pt;
                    color: #95a5a6;
                }}
                
                .dicas {{
                    background: #fff9e6;
                    padding: 12px;
                    margin-top: 20px;
                    border-radius: 5px;
                    font-size: 10pt;
                }}
                
                button {{
                    background: #3498db;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    font-size: 14px;
                    border-radius: 6px;
                    cursor: pointer;
                    margin: 10px 5px;
                }}
                
                button:hover {{
                    background: #2980b9;
                }}
                
                .buttons {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="prova-container">
                <div class="buttons no-print">
                    <button onclick="window.print()">🖨️ Imprimir Prova</button>
                    <button onclick="window.location.href='index.html'">🏠 Voltar para a Arly</button>
                </div>
                
                <div class="header">
                    <h1>📝 {self.materia}</h1>
                    <h2>{self.tema}</h2>
                    <div class="info">
                        Nível: {self.nivel.upper()} | Data: {self.data_geracao}
                    </div>
                </div>
                
                <div class="student-info">
                    <table>
                        <tr>
                            <td>Nome do aluno(a):</td>
                            <td style="border-bottom: 1px solid #000;">_________________________________________</td>
                        </tr>
                        <tr>
                            <td>Data:</td>
                            <td style="border-bottom: 1px solid #000;">___ / ___ / _______</td>
                        </tr>
                        <tr>
                            <td>Total de questões:</td>
                            <td>{len(self.questoes)} questões</td>
                        </tr>
                    </table>
                </div>
        """
        
        # Adiciona resumo se existir
        if self.resumo:
            html += f"""
                <div class="resumo">
                    <h3>📘 Resumo Rápido</h3>
                    <p>{self.resumo}</p>
                </div>
            """
        
        # Adiciona questões
        for q in self.questoes:
            nivel_icon = niveis_icons.get(q["nivel"], "📘")
            tipo_texto = "Múltipla Escolha" if q["tipo"] == "multipla_escolha" else "Questão Discursiva"
            
            html += f"""
                <div class="questao">
                    <div class="questao-header">
                        <span class="questao-numero">Questão {q["numero"]}</span>
                        <span class="questao-nivel">{nivel_icon} {q["nivel"].upper()}</span>
                        <span style="margin-left: 10px; font-size: 9pt; color: #95a5a6;">[{tipo_texto}]</span>
                    </div>
                    
                    <div class="questao-texto">
                        {q["texto"]}
                    </div>
            """
            
            # Alternativas para múltipla escolha
            if q["tipo"] == "multipla_escolha" and q["alternativas"]:
                letras = ["a", "b", "c", "d", "e"]
                html += '<div class="alternativas">'
                for i, alt in enumerate(q["alternativas"]):
                    html += f"""
                        <div class="alternativa">
                            <span class="alternativa-letra">{letras[i]})</span> 
                            {alt}
                        </div>
                    """
                html += '</div>'
            
            # Espaço para resposta
            html += f"""
                    <div class="espaco-resposta">
                        <h4>📝 Espaço para resposta:</h4>
                        <div class="linhas-resposta" style="min-height: {q['espaco_linhas'] * 25}px;"></div>
                    </div>
                </div>
            """
        
        # Rodapé com dicas
        html += f"""
                <div class="footer">
                    <div class="dicas">
                        💡 Dicas importantes:<br>
                        • Leia cada questão com atenção antes de responder<br>
                        • Revise suas respostas ao final<br>
                        • Use o espaço disponível para rascunho<br>
                        • Boa prova! 🌟
                    </div>
                    <p style="margin-top: 15px;">
                        Professora Arly - Sua IA de Química<br>
                        Gerado automaticamente em {self.data_geracao}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def gerar_gabarito_professor_html(self):
        """Gera HTML do gabarito para o professor"""
        
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Gabarito - {self.materia}</title>
            <style>
                @media print {{
                    body {{
                        margin: 0;
                        padding: 20px;
                    }}
                    .no-print {{
                        display: none;
                    }}
                }}
                
                body {{
                    font-family: 'Times New Roman', 'Arial', serif;
                    background: white;
                    padding: 40px;
                    max-width: 900px;
                    margin: 0 auto;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 3px solid #27ae60;
                }}
                
                .header h1 {{
                    color: #27ae60;
                }}
                
                .gabarito-item {{
                    margin-bottom: 30px;
                    padding: 15px;
                    background: #f9f9f9;
                    border-left: 4px solid #27ae60;
                    border-radius: 5px;
                    page-break-inside: avoid;
                }}
                
                .resposta {{
                    background: #e8f5e9;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                
                .explicacao {{
                    color: #555;
                    line-height: 1.6;
                    margin: 10px 0;
                }}
                
                .erros-comuns {{
                    background: #fff3e0;
                    padding: 10px;
                    margin-top: 10px;
                    border-radius: 5px;
                    font-size: 11pt;
                }}
                
                button {{
                    background: #27ae60;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    font-size: 14px;
                    border-radius: 6px;
                    cursor: pointer;
                    margin: 10px 5px;
                }}
                
                button:hover {{
                    background: #229954;
                }}
            </style>
        </head>
        <body>
            <div class="buttons no-print" style="text-align: center; margin-bottom: 20px;">
                <button onclick="window.print()">🖨️ Imprimir Gabarito</button>
                <button onclick="window.location.href='index.html'">🏠 Voltar</button>
            </div>
            
            <div class="header">
                <h1>📖 Gabarito - {self.materia}</h1>
                <h2>{self.tema}</h2>
                <p>Data de geração: {self.data_geracao}</p>
            </div>
            
            <div class="gabarito-container">
        """
        
        for g in self.gabarito:
            html += f"""
                <div class="gabarito-item">
                    <h3>Questão {g['numero']}</h3>
                    <div class="resposta">
                        ✅ Resposta correta: {g['resposta']}
                    </div>
                    <div class="explicacao">
                        <strong>📚 Explicação:</strong><br>
                        {g['explicacao']}
                    </div>
            """
            
            if g.get('erros_comuns'):
                html += f"""
                    <div class="erros-comuns">
                        <strong>⚠️ Erros comuns que os alunos cometem:</strong><br>
                        {', '.join(g['erros_comuns'])}
                    </div>
                """
            
            html += "</div>"
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html