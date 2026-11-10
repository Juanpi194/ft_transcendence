from fastapi import FastAPI

app = FastAPI(title="Transcendence API")


@app.get("/")
def read_root():
    return {"message": "¡Hola desde el backend de ft-transcendence!"}


def main():
    print("Hello from src!")


if __name__ == "__main__":
    main()
