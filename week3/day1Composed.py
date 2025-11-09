import subprocess
from dotenv import load_dotenv
import os
from huggingface_hub import login
from api_clients import create_clients
from IPython.display import display
from diffusers import AutoPipelineForText2Image
import torch

load_dotenv(dotenv_path="C:/Users/paing/LLMProjects/llm_engineering/api_key.env",override=True)
HF_API_KEY = os.getenv('HF_API_KEY')

def operation():
  pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")
  pipe.to("cuda")
  prompt = "A class of students learning AI engineering in a vibrant pop-art style"
  image = pipe(prompt=prompt, num_inference_steps=4, guidance_scale=0.0).images[0]
  display(image)

def HF_login():
  login(HF_API_KEY, add_to_git_credential=True)

def get_GPU_info():
  try:
      gpu_info = subprocess.check_output(
          "wmic path win32_VideoController get name", shell=True
      ).decode()
      print(gpu_info)
  except Exception as e:
      print("Could not retrieve GPU info:", e)


def main():
  get_GPU_info()
  HF_login()


if __name__ == "__main__":
    main()
