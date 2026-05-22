# app_arly.py - PROFESSORA ARLY - CHATBOT EDUCACIONAL
# Versão: 3.1 - CORRIGIDA (Avaliação inteligente de respostas)

import os
import json
import re
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv
from datetime import datetime

from config_arly import (
    EXPLICACAO_QUIMICA_SCHEMA,
    RESOLUCAO_EXERCICIO_SCHEMA,
    CONVERSA_SIMPLES_SCHEMA,
    PROVA_SCHEMA,
    is_casual_conversation,
    is_student_answer,
    get_system_instruction,
    get_personality_greeting,
    EXPLANATION_MODES,
    TEACHING_RULES,
    SOCRATIC_MODE,
    MISTAKE_HANDLING,
    PERSONALITY_STYLES,
    CHEMISTRY_CONFIG
)

from formatador_prova import ProvaENEM

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ ERRO: GEMINI_API_KEY não encontrada")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)
CORS(app)

# ============================================
# CONFIGURAÇÃO DO MODELO
# ============================================

MODELO_PADRAO = "gemini-3.1-flash-lite"
print(f"\n🎯 MODELO EM USO: {MODELO_PADRAO}")
print(f"🧪 Arly - Professora de Química IA\n")

# ============================================
# MEMÓRIA PEDAGÓGICA DO ALUNO
# ============================================

class StudentMemory:
    def __init__(self):
        self.history = []
        self.dificuldades = {}
        self.acertos = {}
        self.nivel_atual = "medio"
        self.personalidade_atual = "professora_amigavel"
        self.ultima_pergunta = None
        self.aguardando_resposta = False
        self.conceitos_vistos = set()
        
    def registrar_interacao(self, pergunta, resposta, acertou=False, conceito=None):
        self.history.append({
            "pergunta": pergunta,
            "resposta": resposta[:200] if resposta else None,
            "acertou": acertou,
            "conceito": conceito,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.history) > 50:
            self.history.pop(0)
        
        if conceito:
            self.conceitos_vistos.add(conceito)
            if acertou:
                self.acertos[conceito] = self.acertos.get(conceito, 0) + 1
            else:
                self.dificuldades[conceito] = self.dificuldades.get(conceito, 0) + 1
    
    def ajustar_nivel(self):
        if len(self.history) < 5:
            return self.nivel_atual
        
        ultimos_acertos = sum(1 for h in self.history[-5:] if h.get("acertou", False))
        
        if ultimos_acertos >= 4:
            if self.nivel_atual == "basico":
                self.nivel_atual = "medio"
            elif self.nivel_atual == "medio":
                self.nivel_atual = "avancado"
        elif ultimos_acertos <= 1:
            if self.nivel_atual == "avancado":
                self.nivel_atual = "medio"
            elif self.nivel_atual == "medio":
                self.nivel_atual = "basico"
        
        return self.nivel_atual

memory = StudentMemory()

# ============================================
# FUNÇÕES PARA GERAR QUESTÕES ESTILO PROVA
# ============================================

def gerar_questao_unica(tema, nivel):
    """Gera uma única questão estilo prova com alternativas"""
    
    niveis_map = {
        "basico": "fácil (fundamental)",
        "medio": "médio (ensino médio)",
        "avancado": "difícil (pré-vestibular)"
    }
    
    prompt = f"""
    Crie uma questão de QUÍMICA sobre o tema: "{tema}"
    
    Nível: {niveis_map.get(nivel, 'médio')}
    
    A questão deve ser estilo ENEM/Vestibular, com enunciado contextualizado e 5 alternativas.
    
    FORMATO OBRIGATÓRIO (JSON):
    {{
        "enunciado": "texto da questão com situação problema...",
        "alternativas": [
            "A) texto da alternativa A",
            "B) texto da alternativa B", 
            "C) texto da alternativa C",
            "D) texto da alternativa D",
            "E) texto da alternativa E"
        ],
        "resposta_correta": "A",
        "explicacao": "explicação detalhada do raciocínio...",
        "dificuldade": "fácil/médio/difícil",
        "tema": "{tema}"
    }}
    
    REGRAS:
    - Enunciado deve ser contextualizado (cotidiano, laboratório, indústria)
    - Apenas UMA alternativa correta
    - Explicação deve ser didática, mostrando o cálculo/raciocínio
    - Use unidades corretas (g, mol, L, etc.)
    - Responda APENAS com o JSON, sem texto adicional
    """
    
    config = types.GenerateContentConfig(
        system_instruction="Você é um gerador profissional de questões de Química estilo ENEM e vestibulares.",
        response_mime_type="application/json",
    )
    
    response = client.models.generate_content(
        model=MODELO_PADRAO,
        contents=prompt,
        config=config,
    )
    
    return response.text

def gerar_lista_questoes(tema, quantidade, nivel):
    """Gera uma lista de questões estilo prova"""
    
    niveis_map = {
        "basico": "fácil",
        "medio": "médio",
        "avancado": "difícil"
    }
    
    prompt = f"""
    Crie uma lista de {quantidade} questões de QUÍMICA sobre o tema: "{tema}"
    
    Nível geral: {niveis_map.get(nivel, 'médio')}
    
    Distribuição sugerida:
    - 30% questões fáceis
    - 50% questões médias  
    - 20% questões difíceis
    
    FORMATO OBRIGATÓRIO (JSON):
    {{
        "questoes": [
            {{
                "numero": 1,
                "enunciado": "texto da questão 1...",
                "alternativas": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
                "resposta_correta": "C",
                "explicacao": "explicação...",
                "dificuldade": "fácil"
            }},
            ...
        ],
        "gabarito": [
            {{"numero": 1, "resposta": "C", "explicacao": "..."}},
            ...
        ]
    }}
    
    REGRAS:
    - Cada questão deve ter enunciado contextualizado
    - Sempre 5 alternativas (A a E)
    - Apenas uma correta por questão
    - Inclua cálculos quando necessário (estequiometria, concentração, pH, etc.)
    - As questões devem ser variadas e interessantes
    """
    
    config = types.GenerateContentConfig(
        system_instruction="Você é um gerador profissional de listas de exercícios de Química.",
        response_mime_type="application/json",
    )
    
    response = client.models.generate_content(
        model=MODELO_PADRAO,
        contents=prompt,
        config=config,
    )
    
    return response.text

def gerar_resposta_simples(mensagem, contexto="conversa"):
    """Gera resposta para conversa casual"""
    
    config = types.GenerateContentConfig(
        system_instruction=f"""
        Você é a Arly, uma professora de Química {PERSONALITY_STYLES[memory.personalidade_atual]['tone']}.
        
        REGRAS:
        - Responda como uma professora conversando com aluno
        - Seja natural, use 2-4 frases
        - Use emojis com moderação
        - Se for saudação, responda calorosamente
        - Se for agradecimento, responda com humildade
        """,
        response_mime_type="application/json",
        response_schema=CONVERSA_SIMPLES_SCHEMA,
    )
    
    response = client.models.generate_content(
        model=MODELO_PADRAO,
        contents=mensagem,
        config=config,
    )
    return response.text

def avaliar_resposta_aluno(resposta_aluno, pergunta_original):
    """Avalia a resposta do aluno de forma inteligente usando o Gemini"""
    
    prompt_avaliacao = f"""
    Você é a Professora Arly, especialista em Química.
    
    PERGUNTA QUE VOCÊ FEZ AO ALUNO:
    "{pergunta_original}"
    
    RESPOSTA DO ALUNO:
    "{resposta_aluno}"
    
    Agora, avalie esta resposta como uma professora atenciosa e educativa.
    
    FORMATO DA RESPOSTA (JSON):
    {{
        "resposta": "Seu feedback para o aluno (parabenize, corrija se necessário, seja encorajador)",
        "pergunta_guia": "Faça uma nova pergunta para aprofundar ou verificar entendimento",
        "dica": "Dê uma dica útil relacionada ao tema"
    }}
    
    REGRAS:
    - Se a resposta estiver correta, parabenize e faça uma pergunta mais desafiadora
    - Se estiver parcialmente correta, destaque o acerto e corrija gentilmente o erro
    - Se estiver errada, não humilhe, explique o porquê e dê uma dica
    - Sempre termine com uma pergunta guia
    - Use linguagem positiva e encorajadora
    """
    
    config = types.GenerateContentConfig(
        system_instruction="Você é uma professora de Química avaliando a resposta de um aluno. Dê feedback educativo e construtivo.",
        response_mime_type="application/json",
        response_schema=CONVERSA_SIMPLES_SCHEMA,
    )
    
    response = client.models.generate_content(
        model=MODELO_PADRAO,
        contents=prompt_avaliacao,
        config=config,
    )
    return response.text

def explicar_conceito(pergunta, nivel):
    """Explica conceito de química de forma didática"""
    
    nivel_ajustado = memory.ajustar_nivel()
    
    # VERIFICAÇÃO CORRIGIDA: Agora avalia resposta de forma inteligente
    if memory.aguardando_resposta and is_student_answer(pergunta, memory.ultima_pergunta):
        print(f"📝 Aluno respondendo à pergunta: {memory.ultima_pergunta}")
        print(f"📝 Resposta do aluno: {pergunta}")
        
        memory.aguardando_resposta = False
        
        # Usa o Gemini para avaliar a resposta de verdade
        resposta_json = avaliar_resposta_aluno(pergunta, memory.ultima_pergunta)
        return resposta_json
    
    if is_casual_conversation(pergunta):
        print(f"💬 Conversa casual: '{pergunta}'")
        return gerar_resposta_simples(pergunta)
    
    print(f"🔬 Explicando conceito: '{pergunta[:50]}...'")
    
    nivel_config = EXPLANATION_MODES.get(nivel_ajustado, EXPLANATION_MODES["medio"])
    
    prompt = f"""
    Pergunta do aluno: {pergunta}
    Nível de ensino: {nivel_ajustado}
    
    Explique o conceito de forma clara e didática.
    
    ESTRUTURA OBRIGATÓRIA:
    1. Definição simples
    2. Explicação detalhada
    3. Exemplo do dia a dia
    4. Pergunta para o aluno verificar entendimento
    """
    
    config = types.GenerateContentConfig(
        system_instruction=get_system_instruction(nivel_ajustado, memory.personalidade_atual),
        response_mime_type="application/json",
        response_schema=EXPLICACAO_QUIMICA_SCHEMA,
    )
    
    response = client.models.generate_content(
        model=MODELO_PADRAO,
        contents=prompt,
        config=config,
    )
    
    resposta_obj = json.loads(response.text)
    
    if "pergunta_para_aluno" in resposta_obj and resposta_obj["pergunta_para_aluno"]:
        memory.ultima_pergunta = resposta_obj["pergunta_para_aluno"]
        memory.aguardando_resposta = True
    
    return response.text

def gerar_prova(materia, tema, nivel, quantidade):
    """Gera prova estilo ENEM"""
    
    prompt = f"""
    Crie uma prova de {materia} com o tema "{tema}" para o nível {nivel}.
    A prova deve ter EXATAMENTE {quantidade} questões.
    
    FORMATO OBRIGATÓRIO (JSON):
    {{
        "resumo": "resumo rápido do conteúdo...",
        "questoes": [
            {{
                "numero": 1,
                "nivel": "fácil/médio/difícil",
                "texto": "enunciado da questão...",
                "tipo": "multipla_escolha",
                "alternativas": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
                "resposta_correta": "B",
                "explicacao": "explicação detalhada..."
            }}
        ]
    }}
    """
    
    config = types.GenerateContentConfig(
        system_instruction="Você é um gerador de provas profissional estilo ENEM.",
        response_mime_type="application/json",
    )
    
    response = client.models.generate_content(
        model=MODELO_PADRAO,
        contents=prompt,
        config=config,
    )
    return json.loads(response.text)

# ============================================
# ENDPOINTS DA API
# ============================================

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status": "success",
        "professora": "Arly",
        "especialidade": "Química",
        "versao": "3.1"
    }), 200

@app.route("/explicar", methods=["POST"])
def explicar():
    data = request.get_json()
    
    if not data or "pergunta" not in data:
        return jsonify({"status": "error", "message": "Envie {'pergunta': 'sua dúvida aqui'}"}), 400
    
    pergunta = data.get("pergunta", "").strip()
    nivel = data.get("nivel", memory.nivel_atual)
    
    if not pergunta:
        return jsonify({"status": "error", "message": "Pergunta não pode estar vazia"}), 400
    
    try:
        resposta_json = explicar_conceito(pergunta, nivel)
        resposta = json.loads(resposta_json)
        
        if "resposta" in resposta and "conceito_principal" not in resposta:
            return jsonify({
                "status": "success",
                "tipo": "conversa",
                "resposta": resposta["resposta"]
            }), 200
        
        return jsonify({
            "status": "success",
            "tipo": "quimica",
            "aula": resposta
        }), 200
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/exercicio", methods=["POST"])
def exercicio():
    """Gera questões estilo prova para o aluno resolver"""
    data = request.get_json()
    
    if not data or "enunciado" not in data:
        return jsonify({
            "status": "error",
            "message": "Envie {'enunciado': 'tópico da questão'}"
        }), 400
    
    try:
        texto = data["enunciado"].strip()
        
        # Detecta se o usuário quer X questões
        match = re.search(r'(\d+)\s*(questões|questoes|exercícios|exercicios)', texto.lower())
        
        if match:
            quantidade = min(int(match.group(1)), 15)
            tema = re.sub(r'\d+\s*(questões|questoes|exercícios|exercicios)', '', texto.lower()).strip()
            if not tema:
                tema = "química geral"
            
            resposta_json = gerar_lista_questoes(tema, quantidade, data.get("nivel", memory.nivel_atual))
            resposta = json.loads(resposta_json)
            
            return jsonify({
                "status": "success",
                "tipo": "lista_questoes",
                "questoes": resposta.get("questoes", []),
                "gabarito": resposta.get("gabarito", []),
                "total": len(resposta.get("questoes", []))
            }), 200
        else:
            resposta_json = gerar_questao_unica(texto, data.get("nivel", memory.nivel_atual))
            resposta = json.loads(resposta_json)
            
            return jsonify({
                "status": "success",
                "tipo": "questao_unica",
                "questao": resposta,
                "total": 1
            }), 200
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/gerar_prova", methods=["POST"])
def prova():
    data = request.get_json()
    
    materia = data.get("materia", "Química")
    tema = data.get("tema", "Geral")
    nivel = data.get("nivel", "médio")
    quantidade = min(data.get("quantidade", 10), 20)
    
    try:
        prova_data = gerar_prova(materia, tema, nivel, quantidade)
        
        return jsonify({
            "status": "success",
            "prova": prova_data,
            "total_questoes": len(prova_data.get("questoes", []))
        }), 200
        
    except Exception as e:
        print(f"❌ Erro ao gerar prova: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset():
    global memory
    memory = StudentMemory()
    return jsonify({"status": "success", "message": "Memória resetada!"}), 200

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "success",
        "nivel_atual": memory.nivel_atual,
        "total_interacoes": len(memory.history)
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)