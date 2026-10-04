from fastapi import FastAPI

from app.api.repository import router as repository_router
from app.api.requirements import router as requirements_router
from app.api.architecture import router as architecture_router
from app.api.code_generation import router as code_generation_router
from app.api.implementation import router as implementation_router
from app.api.testing import router as testing_router
from app.api.test_execution import router as test_execution_router
from app.api.debugging import router as debugging_router
from app.api.code_review import router as code_review_router
from app.api.security import router as security_router
from app.api.performance import router as performance_router
from app.api.deployment import router as deployment_router
from app.api.git import router as git_router
from app.api.git_commit import router as git_commit_router


app = FastAPI(
    title="DEVORA",
    description="Autonomous AI Software Engineering System",
    version="1.0.0"
)


app.include_router(repository_router)
app.include_router(requirements_router)
app.include_router(architecture_router)
app.include_router(code_generation_router)
app.include_router(implementation_router)
app.include_router(testing_router)
app.include_router(test_execution_router)
app.include_router(debugging_router)
app.include_router(code_review_router)
app.include_router(security_router)
app.include_router(performance_router)
app.include_router(deployment_router)
app.include_router(git_router)
app.include_router(git_commit_router)


@app.get("/")
def root():
    return {
        "project": "DEVORA",
        "status": "running",
        "message": "DEVORA AI Software Engineering System is online"
    }