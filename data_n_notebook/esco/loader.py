import pandas as pd
from pathlib import Path

def load_esco(DATA_DIR: Path, limit: int = None):
    print("[LOG] Loading ESCO CSV files from:", DATA_DIR)
    read_opts = dict(dtype=str, keep_default_na=False)

    # Load full files
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

    if limit is not None:
        print(f"[LOG] Truncating ESCO data to first {limit} entries per entity...")
        esco_data["occupations"] = esco_data["occupations"].head(limit)
        esco_data["skills"] = esco_data["skills"].head(limit)
        esco_data["skill_groups"] = esco_data["skill_groups"].head(limit)
        esco_data["isco_groups"] = esco_data["isco_groups"].head(limit)

        # Filter relations to match available nodes
        occ_ids = set(esco_data["occupations"]["ID"])
        skill_ids = set(esco_data["skills"]["ID"])

        esco_data["occupation_to_skill_relations"] = esco_data["occupation_to_skill_relations"][
            esco_data["occupation_to_skill_relations"]["OCCUPATIONID"].isin(occ_ids) &
            esco_data["occupation_to_skill_relations"]["SKILLID"].isin(skill_ids)
        ]

        esco_data["skill_to_skill_relations"] = esco_data["skill_to_skill_relations"][
            esco_data["skill_to_skill_relations"]["REQUIRINGID"].isin(skill_ids) &
            esco_data["skill_to_skill_relations"]["REQUIREDID"].isin(skill_ids)
        ]

        esco_data["skill_hierarchy"] = esco_data["skill_hierarchy"][
            esco_data["skill_hierarchy"]["PARENTID"].isin(skill_ids) &
            esco_data["skill_hierarchy"]["CHILDID"].isin(skill_ids)
        ]

        esco_data["occupation_hierarchy"] = esco_data["occupation_hierarchy"][
            esco_data["occupation_hierarchy"]["PARENTID"].isin(occ_ids) &
            esco_data["occupation_hierarchy"]["CHILDID"].isin(occ_ids)
        ]

    # Build lookup maps for fast access
    esco_data["skills_lookup"] = esco_data["skills"].set_index("ID")["PREFERREDLABEL"].to_dict()
    esco_data["occupations_lookup"] = esco_data["occupations"].set_index("ID")["PREFERREDLABEL"].to_dict()

    return esco_data
