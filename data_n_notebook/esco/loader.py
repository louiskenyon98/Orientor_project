import pandas as pd
from pathlib import Path
def load_esco(DATA_DIR):
    print("[LOG] Loading ESCO CSV files from:", DATA_DIR)
    read_opts = dict(dtype=str, keep_default_na=False)
    esco_data = {
        "occupations": pd.read_csv(DATA_DIR / "occupations.csv", **read_opts),
        "skills": pd.read_csv(DATA_DIR / "skills.csv", **read_opts),
        "skill_groups": pd.read_csv(DATA_DIR / "skill_groups.csv", **read_opts),
        "occupation_to_skill_relations": pd.read_csv(DATA_DIR / "occupation_to_skill_relations.csv", **read_opts),
        "skill_to_skill_relations": pd.read_csv(DATA_DIR / "skill_to_skill_relations.csv", **read_opts),
        "skill_hierarchy": pd.read_csv(DATA_DIR / "skill_hierarchy.csv", **read_opts),
        "occupation_hierarchy": pd.read_csv(DATA_DIR / "occupation_hierarchy.csv", **read_opts),
        "isco_groups": pd.read_csv(DATA_DIR / "occupation_groups.csv", **read_opts),
    }
    # Build lookup maps for fast access
    esco_data['skills_lookup'] = esco_data['skills'].set_index('ID')['PREFERREDLABEL'].to_dict()
    esco_data['occupations_lookup'] = esco_data['occupations'].set_index('ID')['PREFERREDLABEL'].to_dict()
    return esco_data
