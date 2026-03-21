# перед сборкой
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
sudo docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi


# тесты
docker exec -it ollama-server ollama list

docker logs -f vkr-check-worker

docker exec -it vkr-check-worker curl -i http://ollama-server:11434/health

docker exec -it ollama-server ollama run  "Привет"