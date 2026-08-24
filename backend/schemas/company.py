from pydantic import BaseModel


class CompanyDossier(BaseModel):
    """Spiegelt exakt das dict-Format aus
    services/company_research.fetch_company_dossier() sowie das
    Dossier-TS-Interface in frontend/src/pages/CompanyDossierPage.tsx /
    components/CompanyDossier.tsx."""

    company: str
    description: str | None = None
    founded: str | None = None
    employees: str | None = None
    industry: str | None = None
    headquarters: str | None = None
    website: str | None = None
    wikipedia_url: str | None = None
    logo_url: str | None = None
    warning: str | None = None
    source: str
