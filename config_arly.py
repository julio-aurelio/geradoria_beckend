# config_arly.py

# Schema para explicações de química
EXPLICACAO_QUIMICA_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "conceito_principal": {
            "type": "STRING", 
            "description": "O nome do conceito químico que será explicado (ex: 'Ligação Covalente', 'pH', 'Tabela Periódica')"
        },
        "explicacao_simplificada": {
            "type": "STRING",
            "description": "Explicação clara e acessível do conceito, como se estivesse ensinando um aluno do ensino médio"
        },
        "exemplo_pratico": {
            "type": "STRING",
            "description": "Um exemplo do dia a dia que ilustra o conceito químico"
        },
        "formulas_ou_equacoes": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Lista de fórmulas, reações ou equações químicas relevantes ao conceito"
        },
        "pergunta_para_aluno": {
            "type": "STRING",
            "description": "Uma pergunta para testar o entendimento do aluno sobre o conceito explicado"
        },
        "dica_curiosidade": {
            "type": "STRING",
            "description": "Uma curiosidade ou dica de estudo relacionada ao tema"
        }
    },
    "required": ["conceito_principal", "explicacao_simplificada", "exemplo_pratico", 
                 "formulas_ou_equacoes", "pergunta_para_aluno", "dica_curiosidade"]
}

# Schema para resolução de exercícios
RESOLUCAO_EXERCICIO_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "interpretacao_problema": {
            "type": "STRING",
            "description": "Reinterpretação do problema com suas próprias palavras"
        },
        "passo_a_passo": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Cada etapa da resolução explicada detalhadamente"
        },
        "resposta_final": {
            "type": "STRING",
            "description": "Resposta final do exercício com unidade quando aplicável"
        },
        "verificacao_entendimento": {
            "type": "STRING",
            "description": "Pergunta para confirmar se o aluno entendeu a resolução"
        }
    },
    "required": ["interpretacao_problema", "passo_a_passo", "resposta_final", "verificacao_entendimento"]
}

SYSTEM_INSTRUCTION_ARLY = """
Você é a Arly, uma professora de Química apaixonada e paciente, com mais de 15 anos de experiência. 
Sua missão é tornar a química fascinante e compreensível para todos os níveis.

Características da Arly:
- Fala de forma calma, encorajadora e usa analogias criativas
- SEMPRE explica conceitos complexos em linguagem simples primeiro
- Adora fazer conexões com o cotidiano do aluno
- Não julga perguntas "bobas" - todo conhecimento é válido
- Incentiva o pensamento crítico com perguntas instigantes
- Voce não deve de forma alguma fala explicitamente sobre pornografia ou algo que inflija o codigo de eitca e moral ou desrepeite as leis do Brasil, seguindo o codigo de conduta do país realizado a requisição

Você DEVE preencher todos os campos do esquema fornecido estritamente em português brasileiro.
Se o aluno fizer uma pergunta específica, adapte o 'conceito_principal' e todos os campos para responder exatamente àquela dúvida.
"""