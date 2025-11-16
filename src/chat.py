from search import search_prompt

def main():
    """
    Inicia o chat RAG em modo interativo.
    Permite ao usuário fazer perguntas e receber respostas baseadas nos documentos.
    """
    print("=" * 60)
    print("BEM-VINDO AO CHAT RAG (Retrieval-Augmented Generation)")
    print("=" * 60)
    print("\nDigite 'sair' ou 'exit' para encerrar o chat.\n")
    
    while True:
        try:
            # Obter pergunta do usuário
            pergunta = input("Você: ").strip()
            
            # Verificar se o usuário quer sair
            if pergunta.lower() in ['sair', 'exit', 'quit']:
                print("\nEncerrando chat. Até logo!")
                break
            
            # Validar pergunta
            if not pergunta:
                print("Por favor, digite uma pergunta válida.\n")
                continue
            
            # Executar busca e obter resposta
            print("\n[PROCESSANDO...]")
            resposta = search_prompt(question=pergunta)
            
            print(f"\nAssistente: {resposta}\n")
            print("-" * 60 + "\n")
        
        except KeyboardInterrupt:
            print("\n\nChat interrompido pelo usuário. Até logo!")
            break
        except Exception as e:
            print(f"\n[ERRO] {e}\n")
            print("Tente novamente com uma pergunta diferente.\n")

if __name__ == "__main__":
    main()