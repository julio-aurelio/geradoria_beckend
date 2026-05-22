# app_arly.py - USANDO SOMENTE gemini-3-flash-preview

import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

from config_arly import (
    EXPLICACAO_QUIMICA_SCHEMA, 
    SYSTEM_INSTRUCTION_ARLY,
    RESOLUCAO_EXERCICIO_SCHEMA,
    CONVERSA_SIMPLES_SCHEMA,
    is_casual_conversation
)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ ERRO: GEMINI_API_KEY não encontrada")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)
CORS(app)

# ========== MODELO ÚNICO ==========
MODELO = "gemini-3-flash-preview"

# ========== FUNÇÕES ==========

def explicar_conceito(duvida_aluno, nivel="medio"):
    """Gera explicação usando gemini-3-flash-preview"""
    
    # Conversa casual
    if is_casual_conversation(duvida_aluno):
        print(f"💬 Casual: '{duvida_aluno}'")
        
        response = client.models.generate_content(
            model=MODELO,
            contents=duvida_aluno,
            config=types.GenerateContentConfig(
                system_instruction="""
                Você é a Arly, professora de Química.
                Responda de forma natural e amigável (2-4 frases).
                """,
                response_mime_type="application/json",
                response_schema=CONVERSA_SIMPLES_SCHEMA,
            )
        )
        return response.text
    
    # Conceito químico
    print(f"🔬 Química: '{duvida_aluno[:50]}'")
    
    conteudo_prompt = f"""
    Pergunta: {duvida_aluno}
    Nível: {nivel}
    
    Responda de forma completa e didática. Use exemplos reais.
    """
    
    response = client.models.generate_content(
        model=MODELO,
        contents=conteudo_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION_ARLY,
            response_mime_type="application/json",
            response_schema=EXPLICACAO_QUIMICA_SCHEMA,
        )
    )
    return response.text

def resolver_exercicio(enunciado):
    """Resolve exercício"""
    response = client.models.generate_content(
        model=MODELO,
        contents=f"Resolva: {enunciado}",
        config=types.GenerateContentConfig(
            system_instruction="Resolva passo a passo de forma clara.",
            response_mime_type="application/json",
            response_schema=RESOLUCAO_EXERCICIO_SCHEMA,
        )
    )
    return response.text

# ========== ENDPOINTS ==========

@app.route("/")
def root():
    return jsonify({
        "status": "success",
        "professora": "Arly",
        "modelo": MODELO,
        "versao": "3.0"
    }), 200

@app.route("/explicar", methods=["POST"])
def explicar():
    data = request.get_json()
    
    if not data or "pergunta" not in data:
        return jsonify({"status": "error", "message": "Envie {'pergunta': '...'}"}), 400
    
    pergunta = data.get("pergunta", "").strip()
    nivel = data.get("nivel", "medio")
    
    if not pergunta:
        return jsonify({"status": "error", "message": "Pergunta vazia"}), 400
    
    try:
        resposta_json = explicar_conceito(pergunta, nivel)
        resposta = json.loads(resposta_json)
        
        if "resposta" in resposta:
            return jsonify({"status": "success", "tipo": "conversa", "resposta": resposta["resposta"]}), 200
        else:
            return jsonify({"status": "success", "tipo": "quimica", "aula": resposta}), 200
            
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/exercicio", methods=["POST"])
def exercicio():
    data = request.get_json()
    
    if not data or "enunciado" not in data:
        return jsonify({"status": "error", "message": "Envie {'enunciado': '...'}"}), 400
    
    try:
        resposta_json = resolver_exercicio(data["enunciado"])
        resposta = json.loads(resposta_json)
        return jsonify({"status": "success", "tipo": "exercicio", "resolucao": resposta}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print(f"🚀 Rodando com modelo: {MODELO}")
    app.run(debug=True, host="0.0.0.0", port=5000)