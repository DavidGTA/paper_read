from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import papers, relation_types, paper_relations
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(papers.router, prefix=f"{settings.API_V1_STR}/papers", tags=["papers"])
app.include_router(relation_types.router, prefix=f"{settings.API_V1_STR}/relation-types", tags=["relation_types"])
app.include_router(paper_relations.router, prefix=f"{settings.API_V1_STR}/paper-relations", tags=["paper_relations"])
