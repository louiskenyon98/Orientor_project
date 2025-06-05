#!/usr/bin/env python3
"""
Script de validation des données HEXACO-PI-R
Valide la structure des fichiers CSV et la configuration sans dépendances externes
"""

import os
import sys
import json
import csv
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

class HexacoDataValidator:
    """Validateur pour les données HEXACO sans dépendances externes."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_path = self.project_root / "data_n_notebook" / "data"
        self.config_path = self.project_root / "backend" / "app" / "config" / "hexaco_facet_mapping.json"
        self.test_results = {
            "data_files": {},
            "configuration": {},
            "data_integrity": {},
            "structure_validation": {}
        }
        
    def log_test(self, category: str, test_name: str, success: bool, details: str = ""):
        """Enregistre le résultat d'un test."""
        self.test_results[category][test_name] = {
            "success": success,
            "details": details,
            "timestamp": time.time()
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} [{category}] {test_name}: {details}")
    
    def test_file_existence(self):
        """Teste l'existence des fichiers requis."""
        print("\n🔍 Test de l'existence des fichiers...")
        
        # Fichiers CSV requis
        required_csv_files = [
            "French_60_FULL.csv",
            "French_100_FULL.csv", 
            "English_60_FULL.csv",
            "English_100_FULL.csv"
        ]
        
        for csv_file in required_csv_files:
            file_path = self.data_path / csv_file
            if file_path.exists():
                file_size = file_path.stat().st_size
                self.log_test("data_files", f"{csv_file}_exists", True, 
                            f"Fichier trouvé ({file_size} bytes)")
            else:
                self.log_test("data_files", f"{csv_file}_exists", False, 
                            "Fichier manquant")
        
        # Fichier de configuration
        if self.config_path.exists():
            self.log_test("data_files", "config_exists", True, 
                        "Configuration trouvée")
        else:
            self.log_test("data_files", "config_exists", False, 
                        "Configuration manquante")
    
    def test_configuration_structure(self):
        """Teste la structure de la configuration HEXACO."""
        print("\n⚙️ Test de la structure de configuration...")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Vérifier les sections principales
            required_sections = ["domains", "versions", "languages"]
            for section in required_sections:
                if section in config:
                    self.log_test("configuration", f"{section}_section", True, 
                                f"Section {section} présente")
                else:
                    self.log_test("configuration", f"{section}_section", False, 
                                f"Section {section} manquante")
            
            # Vérifier les domaines HEXACO
            if "domains" in config:
                expected_domains = [
                    "Honesty-Humility", "Emotionality", "Extraversion",
                    "Agreeableness", "Conscientiousness", "Openness"
                ]
                
                actual_domains = list(config["domains"].keys())
                missing_domains = [d for d in expected_domains if d not in actual_domains]
                
                if not missing_domains:
                    self.log_test("configuration", "domains_complete", True, 
                                f"6 domaines HEXACO présents")
                else:
                    self.log_test("configuration", "domains_complete", False, 
                                f"Domaines manquants: {missing_domains}")
            
            # Vérifier les versions
            if "versions" in config:
                expected_versions = [
                    "hexaco_60_fr", "hexaco_100_fr", 
                    "hexaco_60_en", "hexaco_100_en"
                ]
                
                actual_versions = list(config["versions"].keys())
                missing_versions = [v for v in expected_versions if v not in actual_versions]
                
                if not missing_versions:
                    self.log_test("configuration", "versions_complete", True, 
                                f"4 versions configurées")
                else:
                    self.log_test("configuration", "versions_complete", False, 
                                f"Versions manquantes: {missing_versions}")
            
        except Exception as e:
            self.log_test("configuration", "config_parsing", False, str(e))
    
    def test_csv_structure(self):
        """Teste la structure des fichiers CSV."""
        print("\n📊 Test de la structure des fichiers CSV...")
        
        required_columns = [
            "item_id", "item_text", "response_min", "response_max",
            "version", "language", "reverse_keyed", "facet"
        ]
        
        csv_files = [
            ("French_60_FULL.csv", 60, "french"),
            ("French_100_FULL.csv", 100, "french"),
            ("English_60_FULL.csv", 60, "english"),
            ("English_100_FULL.csv", 100, "english")
        ]
        
        for csv_file, expected_count, expected_language in csv_files:
            file_path = self.data_path / csv_file
            
            if not file_path.exists():
                self.log_test("data_integrity", f"{csv_file}_structure", False, 
                            "Fichier non trouvé")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    # Vérifier les colonnes
                    actual_columns = reader.fieldnames
                    missing_columns = [col for col in required_columns if col not in actual_columns]
                    
                    if missing_columns:
                        self.log_test("data_integrity", f"{csv_file}_columns", False, 
                                    f"Colonnes manquantes: {missing_columns}")
                        continue
                    
                    # Compter les lignes et valider les données
                    rows = list(reader)
                    actual_count = len(rows)
                    
                    if actual_count == expected_count:
                        self.log_test("data_integrity", f"{csv_file}_count", True, 
                                    f"{actual_count} questions")
                    else:
                        self.log_test("data_integrity", f"{csv_file}_count", False, 
                                    f"Attendu: {expected_count}, Trouvé: {actual_count}")
                    
                    # Valider quelques lignes
                    validation_errors = []
                    for i, row in enumerate(rows[:5]):  # Valider les 5 premières lignes
                        try:
                            # Vérifier item_id
                            item_id = int(row["item_id"])
                            if item_id < 1:
                                validation_errors.append(f"Ligne {i+1}: item_id invalide")
                            
                            # Vérifier response_min/max
                            response_min = int(row["response_min"])
                            response_max = int(row["response_max"])
                            if response_min != 1 or response_max != 5:
                                validation_errors.append(f"Ligne {i+1}: échelle de réponse invalide")
                            
                            # Vérifier reverse_keyed
                            reverse_keyed = row["reverse_keyed"].lower()
                            if reverse_keyed not in ["true", "false"]:
                                validation_errors.append(f"Ligne {i+1}: reverse_keyed invalide")
                            
                            # Vérifier la langue
                            language = row["language"].lower()
                            if language != expected_language:
                                validation_errors.append(f"Ligne {i+1}: langue incorrecte")
                                
                        except ValueError as e:
                            validation_errors.append(f"Ligne {i+1}: erreur de format - {e}")
                    
                    if not validation_errors:
                        self.log_test("data_integrity", f"{csv_file}_validation", True, 
                                    "Structure des données valide")
                    else:
                        self.log_test("data_integrity", f"{csv_file}_validation", False, 
                                    f"Erreurs: {validation_errors[:3]}")  # Afficher les 3 premières erreurs
                        
            except Exception as e:
                self.log_test("data_integrity", f"{csv_file}_parsing", False, str(e))
    
    def test_facet_mapping(self):
        """Teste la cohérence entre les facettes dans les CSV et la configuration."""
        print("\n🔗 Test de la cohérence des facettes...")
        
        try:
            # Charger la configuration
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Extraire toutes les facettes de la configuration
            config_facets = set()
            if "domains" in config:
                for domain_config in config["domains"].values():
                    if "facets" in domain_config:
                        config_facets.update(domain_config["facets"])
            
            # Extraire les facettes des fichiers CSV
            csv_facets = set()
            csv_files = ["French_60_FULL.csv", "English_60_FULL.csv"]
            
            for csv_file in csv_files:
                file_path = self.data_path / csv_file
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            csv_facets.add(row["facet"])
            
            # Comparer les ensembles
            missing_in_config = csv_facets - config_facets
            missing_in_csv = config_facets - csv_facets
            
            if not missing_in_config and not missing_in_csv:
                self.log_test("structure_validation", "facet_consistency", True, 
                            f"{len(config_facets)} facettes cohérentes")
            else:
                details = []
                if missing_in_config:
                    details.append(f"Manquantes dans config: {missing_in_config}")
                if missing_in_csv:
                    details.append(f"Manquantes dans CSV: {missing_in_csv}")
                
                self.log_test("structure_validation", "facet_consistency", False, 
                            "; ".join(details))
                
        except Exception as e:
            self.log_test("structure_validation", "facet_mapping_error", False, str(e))
    
    def test_reverse_keyed_distribution(self):
        """Teste la distribution des items inversés."""
        print("\n🔄 Test de la distribution des items inversés...")
        
        csv_files = ["French_60_FULL.csv", "English_60_FULL.csv"]
        
        for csv_file in csv_files:
            file_path = self.data_path / csv_file
            
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                
                total_items = len(rows)
                reverse_items = sum(1 for row in rows if row["reverse_keyed"].lower() == "true")
                normal_items = total_items - reverse_items
                
                reverse_percentage = (reverse_items / total_items * 100) if total_items > 0 else 0
                
                # Une bonne distribution devrait avoir environ 30-70% d'items inversés
                if 20 <= reverse_percentage <= 80:
                    self.log_test("structure_validation", f"{csv_file}_reverse_distribution", True, 
                                f"{reverse_items}/{total_items} inversés ({reverse_percentage:.1f}%)")
                else:
                    self.log_test("structure_validation", f"{csv_file}_reverse_distribution", False, 
                                f"Distribution déséquilibrée: {reverse_percentage:.1f}% inversés")
                    
            except Exception as e:
                self.log_test("structure_validation", f"{csv_file}_reverse_error", False, str(e))
    
    def test_version_consistency(self):
        """Teste la cohérence entre les versions configurées et les fichiers CSV."""
        print("\n🔧 Test de cohérence des versions...")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if "versions" not in config:
                self.log_test("structure_validation", "version_config_missing", False, 
                            "Section versions manquante")
                return
            
            for version_id, version_config in config["versions"].items():
                csv_filename = version_config.get("csv_file")
                expected_count = version_config.get("item_count")
                expected_language = version_config.get("language")
                
                if not csv_filename:
                    self.log_test("structure_validation", f"{version_id}_csv_config", False, 
                                "csv_file non configuré")
                    continue
                
                csv_path = self.data_path / csv_filename
                
                if not csv_path.exists():
                    self.log_test("structure_validation", f"{version_id}_csv_exists", False, 
                                f"Fichier {csv_filename} manquant")
                    continue
                
                # Vérifier le nombre d'items
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    actual_count = len(list(reader))
                
                if actual_count == expected_count:
                    self.log_test("structure_validation", f"{version_id}_item_count", True, 
                                f"{actual_count} items")
                else:
                    self.log_test("structure_validation", f"{version_id}_item_count", False, 
                                f"Attendu: {expected_count}, Trouvé: {actual_count}")
                    
        except Exception as e:
            self.log_test("structure_validation", "version_consistency_error", False, str(e))
    
    def generate_report(self):
        """Génère un rapport de validation détaillé."""
        print("\n📊 Génération du rapport de validation...")
        
        report = {
            "timestamp": time.time(),
            "summary": {},
            "details": self.test_results
        }
        
        # Calcul des statistiques par catégorie
        for category, tests in self.test_results.items():
            total_tests = len(tests)
            passed_tests = sum(1 for test in tests.values() if test["success"])
            
            report["summary"][category] = {
                "total": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            }
        
        # Sauvegarde du rapport
        report_path = Path(__file__).parent / "hexaco_data_validation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Rapport sauvegardé: {report_path}")
        
        # Affichage du résumé
        print("\n📈 Résumé de la validation:")
        total_tests = sum(stats["total"] for stats in report["summary"].values())
        total_passed = sum(stats["passed"] for stats in report["summary"].values())
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        for category, stats in report["summary"].items():
            print(f"  {category}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1f}%)")
        
        print(f"\n🎯 Taux de réussite global: {total_passed}/{total_tests} ({overall_success_rate:.1f}%)")
        
        return report
    
    def run_all_validations(self):
        """Exécute toutes les validations."""
        print("🚀 Démarrage de la validation des données HEXACO-PI-R")
        print("=" * 60)
        
        # Tests de base
        self.test_file_existence()
        self.test_configuration_structure()
        
        # Tests de structure des données
        self.test_csv_structure()
        
        # Tests de cohérence
        self.test_facet_mapping()
        self.test_reverse_keyed_distribution()
        self.test_version_consistency()
        
        # Génération du rapport
        report = self.generate_report()
        
        print("\n" + "=" * 60)
        print("✅ Validation des données terminée")
        
        return report

def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validation des données HEXACO-PI-R")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Mode verbeux")
    
    args = parser.parse_args()
    
    validator = HexacoDataValidator()
    report = validator.run_all_validations()
    
    # Code de sortie basé sur les résultats
    total_failed = sum(stats["failed"] for stats in report["summary"].values())
    sys.exit(0 if total_failed == 0 else 1)

if __name__ == "__main__":
    main()