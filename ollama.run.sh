docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama alpine/ollama
docker exec -it ollama ollama pull llama3.2