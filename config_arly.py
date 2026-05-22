# config_arly.py - VERSÃO COMPLETA OTIMIZADA

# Schema para conversa casual
CONVERSA_SIMPLES_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "resposta": {
            "type": "STRING",
            "description": "Resposta curta, amigável e natural (máximo 2 frases)"
        }
    },
    "required": ["resposta"]
}

# Schema para explicações de química (OTIMIZADO)
EXPLICACAO_QUIMICA_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "conceito_principal": {
            "type": "STRING", 
            "description": "Nome do conceito químico"
        },
        "explicacao_simplificada": {
            "type": "STRING",
            "description": "Explicação direta e clara (proporcional à pergunta)"
        },
        "exemplo_pratico": {
            "type": "STRING",
            "description": "Exemplo do dia a dia (apenas se relevante)"
        },
        "formulas_ou_equacoes": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Fórmulas relevantes (opcional)"
        },
        "pergunta_para_aluno": {
            "type": "STRING",
            "description": "Pergunta para reflexão (opcional)"
        },
        "dica_curiosidade": {
            "type": "STRING",
            "description": "Curiosidade rápida (opcional)"
        }
    },
    "required": ["conceito_principal", "explicacao_simplificada"]
}

# Schema para exercícios
RESOLUCAO_EXERCICIO_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "interpretacao_problema": {
            "type": "STRING",
            "description": "Reinterpretação do problema"
        },
        "passo_a_passo": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Passos da resolução (máximo 5)"
        },
        "resposta_final": {
            "type": "STRING",
            "description": "Resposta final direta"
        },
        "verificacao_entendimento": {
            "type": "STRING",
            "description": "Pergunta de verificação (opcional)"
        }
    },
    "required": ["interpretacao_problema", "passo_a_passo", "resposta_final"]
}

SYSTEM_INSTRUCTION_ARLY = """
Você é a Arly, professora de Química direta e eficiente.

REGRAS DE RESPOSTA:
- "Oi", "Olá" → responda com 1-2 frases amigáveis
- "Obrigado" → "Por nada! 😊" ou similar
- Perguntas simples → respostas curtas (2-3 frases)
- Conceitos complexos → explicação detalhada mas sem enrolação

Sempre use português brasileiro e seja educada.
"""

def is_casual_conversation(message):
    """Detecta conversa casual"""
    casual = ["oi", "olá", "ola", "e ai", "opa", "tudo bem", "como vai", 
              "beleza", "obrigado", "valeu", "obg", "vlw", "blz"]
    msg = message.lower().strip()
    return any(p in msg for p in casual)