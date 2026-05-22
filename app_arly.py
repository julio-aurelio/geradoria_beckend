# app_arly.py - VERSÃO COM MODELOS CORRETOS

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
    CONVERSA_SIMPLES_SCHEMA,
    is_casual_conversation
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
CORS(app)

# ========== FUNÇÕES DA ARLY ==========

def explicar_conceito(duvida_aluno, nivel="medio"):
    """
    Gera uma explicação química baseada na dúvida do aluno.
    """
    
    # DETECÇÃO DE CONVERSA CASUAL
    if is_casual_conversation(duvida_aluno):
        print(f"💬 Conversa casual detectada: '{duvida_aluno}' → resposta rápida")
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",  # ✅ MODELO DISPONÍVEL
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
    
    # CONCEITO QUÍMICO NORMAL
    print(f"🔬 Conceito químico detectado: '{duvida_aluno[:50]}...' → resposta detalhada")
    
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
        model="gemini-2.0-flash-exp",  # ✅ MODELO DISPONÍVEL
        contents=conteudo_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION_ARLY,
            response_mime_type="application/json",
            response_schema=EXPLICACAO_QUIMICA_SCHEMA,
        )
    )
    return response.text

def resolver_exercicio(enunciado):
    """Função extra para resolução passo a passo de exercícios"""
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",  # ✅ MODELO DISPONÍVEL
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
        "message": "API funcionando!",
        "versao": "2.0",
        "endpoints": {
            "/explicar": "POST - Envie {'pergunta': 'sua duvida', 'nivel': 'basico/medio/avancado'}",
            "/exercicio": "POST - Envie {'enunciado': 'texto do exercicio'}",
        }
    }), 200

@app.route("/explicar", methods=["POST"])
def explicar():
    """Endpoint principal para tirar dúvidas de química"""
    data = request.get_json()
    
    if not data or "pergunta" not in data:
        return jsonify({
            "status": "error",
            "message": "Envie no formato: {'pergunta': 'O que é pH?'}"
        }), 400
    
    pergunta = data.get("pergunta", "").strip()
    nivel = data.get("nivel", "medio")
    
    if not pergunta:
        return jsonify({
            "status": "error",
            "message": "A pergunta não pode estar vazia."
        }), 400
    
    if nivel not in ["basico", "medio", "avancado"]:
        return jsonify({
            "status": "error",
            "message": "Nível inválido. Use: 'basico', 'medio' ou 'avancado'"
        }), 400
    
    try:
        explicacao_json_string = explicar_conceito(pergunta, nivel)
        explicacao_estruturada = json.loads(explicacao_json_string)
        
        if "resposta" in explicacao_estruturada:
            return jsonify({
                "status": "success",
                "tipo": "conversa",
                "resposta": explicacao_estruturada["resposta"]
            }), 200
        else:
            return jsonify({
                "status": "success",
                "tipo": "quimica",
                "aula": explicacao_estruturada
            }), 200
        
    except Exception as e:
        print(f"Erro detalhado: {e}")
        return jsonify({
            "status": "error",
            "message": f"Erro: {str(e)}"
        }), 500

@app.route("/exercicio", methods=["POST"])
def exercicio():
    """Endpoint para resolver exercícios"""
    data = request.get_json()
    
    if not data or "enunciado" not in data:
        return jsonify({
            "status": "error",
            "message": "Envie no formato: {'enunciado': 'Calcule...'}"
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
            "tipo": "exercicio",
            "resolucao": resolucao_estruturada
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro: {str(e)}"
        }), 500

# ========== EXECUÇÃO ==========
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)