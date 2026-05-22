# app_arly.py - VERSÃO OTIMIZADA COM CONVERSA CASUAL

import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Importando os schemas atualizados
from config_arly import (
    EXPLICACAO_QUIMICA_SCHEMA, 
    SYSTEM_INSTRUCTION_ARLY,
    RESOLUCAO_EXERCICIO_SCHEMA,
    CONVERSA_SIMPLES_SCHEMA,  # NOVO!
    is_casual_conversation      # NOVO!
)

# Carrega as variáveis de ambiente e inicia o Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Verificação crítica da API key
if not GEMINI_API_KEY:
    print("❌ ERRO: GEMINI_API_KEY não encontrada no arquivo .env")
    print("📝 Crie um arquivo .env com: GEMINI_API_KEY=sua_chave_aqui")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# Inicializa o Flask
app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# ========== FUNÇÕES DA ARLY ==========

def explicar_conceito(duvida_aluno, nivel="medio"):
    """
    Gera uma explicação química baseada na dúvida do aluno.
    Versão INTELIGENTE que detecta conversa casual e otimiza resposta.
    
    Parâmetros:
    - duvida_aluno: string com a pergunta ou conceito a ser explicado
    - nivel: "basico", "medio" ou "avancado"
    """
    
    # 🔥 DETECÇÃO DE CONVERSA CASUAL
    if is_casual_conversation(duvida_aluno):
        print(f"💬 Conversa casual detectada: '{duvida_aluno}' → resposta rápida")
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",  # Modelo rápido
            contents=duvida_aluno,
            config=types.GenerateContentConfig(
                system_instruction="""
                Você é a Arly, uma professora de Química amigável e direta.
                
                REGRAS IMPORTANTES:
                - Responda de forma EXTREMAMENTE CURTA (máximo 15 palavras)
                - Se for "oi", "olá" → "Olá! Como posso ajudar? 😊"
                - Se for "obrigado" → "Por nada! 😊"
                - Se for "tudo bem" → "Tudo ótimo! E você?"
                - Seja natural e calorosa, mas sem floreios
                """,
                response_mime_type="application/json",
                response_schema=CONVERSA_SIMPLES_SCHEMA,
            )
        )
        return response.text
    
    # 🧪 CONCEITO QUÍMICO NORMAL (OTIMIZADO)
    print(f"🔬 Conceito químico detectado: '{duvida_aluno[:50]}...' → resposta detalhada")
    
    # Prompt mais direto para economizar tokens
    conteudo_prompt = f"""
    Responda de forma DIRETA e PROPORCIONAL à pergunta.
    
    Pergunta do aluno: {duvida_aluno}
    Nível de ensino: {nivel}
    
    REGRAS:
    - Se for pergunta simples (ex: "o que é pH?"), resposta curta (2-3 frases)
    - Se for conceito complexo, explique detalhadamente mas sem enrolação
    - Campos opcionais (exemplo, fórmulas, pergunta, dica) só preencha se realmente relevantes
    - Mantenha a explicação clara e acessível
    """
    
    response = client.models.generate_content(
        model="gemini-1.5-flash",  # Mudado para modelo estável e rápido
        contents=conteudo_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION_ARLY,
            response_mime_type="application/json",
            response_schema=EXPLICACAO_QUIMICA_SCHEMA,
        )
    )
    return response.text

def resolver_exercicio(enunciado):
    """Função extra para resolução passo a passo de exercícios (OTIMIZADA)"""
    response = client.models.generate_content(
        model="gemini-1.5-flash",  # Padronizado para flash (mais rápido)
        contents=f"Resolva este exercício de química: {enunciado}",
        config=types.GenerateContentConfig(
            system_instruction="""
            Você é a Arly, professora de Química.
            Resolva o exercício de forma clara e objetiva.
            - Máximo 5 passos para resolução
            - Resposta final direta
            - Use linguagem simples
            """,
            response_mime_type="application/json",
            response_schema=RESOLUCAO_EXERCICIO_SCHEMA,
        )
    )
    return response.text

# ========== ENDPOINTS DA API ==========

@app.route("/")
def root():
    return jsonify({
        "status": "success",
        "professora": "Arly - Professora de Química IA",
        "message": "API funcionando! Use /explicar para tirar dúvidas ou /exercicio para resolver problemas.",
        "versao": "2.0",
        "recursos": {
            "conversa_casual": "Respostas rápidas para saudações",
            "explicacoes": "Explicações proporcionais à pergunta",
            "exercicios": "Resolução passo a passo"
        },
        "endpoints": {
            "/explicar": "POST - Envie {'pergunta': 'sua duvida', 'nivel': 'basico/medio/avancado'}",
            "/exercicio": "POST - Envie {'enunciado': 'texto do exercicio'}",
            "/quimica/aleatoria": "GET - Gera um conceito químico aleatório"
        }
    }), 200

@app.route("/explicar", methods=["POST"])
def explicar():
    """Endpoint principal para tirar dúvidas de química (INTELIGENTE)"""
    data = request.get_json()
    
    # Validação 1: O JSON foi enviado?
    if not data or "pergunta" not in data:
        return jsonify({
            "status": "error",
            "message": "Por favor, envie sua pergunta no formato: {'pergunta': 'O que é pH?'}"
        }), 400
    
    pergunta = data.get("pergunta", "").strip()
    nivel = data.get("nivel", "medio")
    
    # Validação 2: A pergunta não está vazia
    if not pergunta:
        return jsonify({
            "status": "error",
            "message": "A pergunta não pode estar vazia."
        }), 400
    
    # Validação 3: Nível válido
    if nivel not in ["basico", "medio", "avancado"]:
        return jsonify({
            "status": "error",
            "message": "Nível inválido. Use: 'basico', 'medio' ou 'avancado'"
        }), 400
    
    try:
        # Gera a explicação da Arly (agora com detecção inteligente)
        explicacao_json_string = explicar_conceito(pergunta, nivel)
        explicacao_estruturada = json.loads(explicacao_json_string)
        
        # Verifica se é uma resposta de conversa casual (schema simples)
        if "resposta" in explicacao_estruturada:
            # Resposta casual
            return jsonify({
                "status": "success",
                "professora": "Arly",
                "tipo": "conversa",
                "pergunta_do_aluno": pergunta,
                "resposta": explicacao_estruturada["resposta"]
            }), 200
        else:
            # Resposta de química normal
            return jsonify({
                "status": "success",
                "professora": "Arly",
                "tipo": "quimica",
                "pergunta_do_aluno": pergunta,
                "nivel": nivel,
                "aula": explicacao_estruturada
            }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao gerar explicação: {str(e)}",
            "dica": "Tente reformular sua pergunta de forma mais clara."
        }), 500

@app.route("/exercicio", methods=["POST"])
def exercicio():
    """Endpoint para resolver exercícios de química"""
    data = request.get_json()
    
    if not data or "enunciado" not in data:
        return jsonify({
            "status": "error",
            "message": "Envie o enunciado no formato: {'enunciado': 'Calcule a massa molar do H2O...'}"
        }), 400
    
    enunciado = data.get("enunciado", "").strip()
    
    if not enunciado:
        return jsonify({
            "status": "error",
            "message": "O enunciado não pode estar vazio."
        }), 400
    
    try:
        resolucao_json_string = resolver_exercicio(enunciado)
        resolucao_estruturada = json.loads(resolucao_json_string)
        
        return jsonify({
            "status": "success",
            "professora": "Arly",
            "tipo": "exercicio",
            "exercicio": enunciado,
            "resolucao": resolucao_estruturada
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao resolver exercício: {str(e)}"
        }), 500

@app.route("/quimica/aleatoria", methods=["GET"])
def conceito_aleatorio():
    """Gera um conceito químico aleatório para estudo"""
    conceitos = [
        "O que é uma ligação iônica?",
        "Explique a tabela periódica",
        "Como funciona o pH?",
        "O que são ácidos e bases?",
        "Explique a lei de Lavoisier",
        "O que é catálise?",
        "Diferença entre solução saturada e insaturada",
        "O que é número de oxidação?",
        "Explique a radioatividade",
        "Como funciona a eletrólise?"
    ]
    
    import random
    pergunta_aleatoria = random.choice(conceitos)
    
    try:
        explicacao_json_string = explicar_conceito(pergunta_aleatoria, "medio")
        explicacao_estruturada = json.loads(explicacao_json_string)
        
        return jsonify({
            "status": "success",
            "professora": "Arly",
            "tipo": "quimica",
            "conceito_do_dia": pergunta_aleatoria,
            "aula": explicacao_estruturada
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro: {str(e)}"
        }), 500

# ========== EXECUÇÃO DO SERVIDOR ==========
if __name__ == "__main__":    
    app.run(debug=True)