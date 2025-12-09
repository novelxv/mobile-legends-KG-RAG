import re
import os
from neo4j import GraphDatabase
from config import load_config

class PrologToGraph:
    def __init__(self, uri=None, auth=None, config_path="config.toml", prolog_dir="prolog_facts"):
        """
        Inisialisasi koneksi ke Neo4j.
        Jika uri dan auth tidak diberikan, akan membaca dari config.toml
        
        Args:
            uri: Neo4j URI (optional, akan baca dari config jika None)
            auth: Neo4j auth tuple (optional, akan baca dari config jika None)
            config_path: Path ke file config.toml
            prolog_dir: Directory tempat file-file prolog berada
        """
        if uri is None or auth is None:
            config = load_config(config_path)
            driver_kwargs = config.get_neo4j_driver_kwargs()
            self.driver = GraphDatabase.driver(**driver_kwargs)
        else:
            self.driver = GraphDatabase.driver(uri, auth=auth)
        
        self.prolog_dir = prolog_dir

    def close(self):
        self.driver.close()

    def parse_prolog_file(self, filename):
        """
        Membaca file .pl dari directory prolog_facts dan mengembalikan list tuple (predikat, arg1, arg2)
        
        Args:
            filename: Nama file prolog (contoh: "hero.pl")
        """
        filepath = os.path.join(self.prolog_dir, filename)
        facts = []
        
        if not os.path.exists(filepath):
            print(f"Warning: File {filepath} tidak ditemukan. Melewati...")
            return facts
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            pattern = re.compile(r"([a-z_]+)\(([\w_]+)(?:,\s*([\w_]+))?\)\.")
            matches = pattern.findall(content)
            for match in matches:
                predicate = match[0]
                arg1 = match[1]
                arg2 = match[2] if match[2] else None
                facts.append((predicate, arg1, arg2))
        return facts

    def ingest_data(self):
        with self.driver.session() as session:
            # LOAD HEROES (Base Nodes)
            print("Loading Heroes...")
            heroes = self.parse_prolog_file("hero.pl")
            for pred, hero_name, _ in heroes:
                if pred == "hero":
                    session.run("MERGE (h:Hero {id: $name, name: replace($name, '_', ' ')})", name=hero_name)

            # LOAD ROLES
            print("Loading Roles...")
            roles = self.parse_prolog_file("role.pl")
            for pred, hero_name, role_name in roles:
                if pred == "memiliki_role":
                    session.run("MERGE (r:Role {id: $rname, name: replace($rname, '_', ' ')})", rname=role_name)
                    session.run("""
                        MATCH (h:Hero {id: $hname}), (r:Role {id: $rname})
                        MERGE (h)-[:HAS_ROLE]->(r)
                    """, hname=hero_name, rname=role_name)

            # LOAD LANES
            print("Loading Lanes...")
            lanes = self.parse_prolog_file("lane.pl")
            for pred, hero_name, lane_name in lanes:
                if pred == "memiliki_lane":
                    session.run("MERGE (l:Lane {id: $lname, name: replace($lname, '_', ' ')})", lname=lane_name)
                    session.run("""
                        MATCH (h:Hero {id: $hname}), (l:Lane {id: $lname})
                        MERGE (h)-[:SUITED_FOR]->(l)
                    """, hname=hero_name, lname=lane_name)

            # LOAD SPECIALTIES
            print("Loading Specialties...")
            specs = self.parse_prolog_file("specialty.pl")
            for pred, hero_name, spec_name in specs:
                if pred == "has_specialty":
                    session.run("MERGE (s:Specialty {id: $sname, name: replace($sname, '_', ' ')})", sname=spec_name)
                    session.run("""
                        MATCH (h:Hero {id: $hname}), (s:Specialty {id: $sname})
                        MERGE (h)-[:HAS_SPECIALTY]->(s)
                    """, hname=hero_name, sname=spec_name)

            # LOAD DAMAGE TYPE
            print("Loading Damage Types...")
            dtypes = self.parse_prolog_file("damage_type.pl")
            for pred, hero_name, dtype in dtypes:
                if pred == "memiliki_damage_type" and dtype != 'true': # Skip fakta 'true'
                    session.run("MERGE (d:DamageType {id: $dname})", dname=dtype)
                    session.run("""
                        MATCH (h:Hero {id: $hname}), (d:DamageType {id: $dname})
                        MERGE (h)-[:DEALS_DAMAGE]->(d)
                    """, hname=hero_name, dname=dtype)

            # LOAD COUNTERS (Hero ke Hero)
            print("Loading Counters...")
            counters = self.parse_prolog_file("counter.pl")
            for pred, hero1, hero2 in counters:
                if pred == "iscounter":
                    session.run("""
                        MATCH (h1:Hero {id: $n1}), (h2:Hero {id: $n2})
                        MERGE (h1)-[:COUNTERS]->(h2)
                    """, n1=hero1, n2=hero2)

            # LOAD COMPATIBILITY (Hero ke Hero)
            print("Loading Compatibility...")
            comps = self.parse_prolog_file("compatible.pl")
            for pred, hero1, hero2 in comps:
                if pred == "compatible":
                    session.run("""
                        MATCH (h1:Hero {id: $n1}), (h2:Hero {id: $n2})
                        MERGE (h1)-[:COMPATIBLE_WITH]->(h2)
                    """, n1=hero1, n2=hero2)

        print("Data ingestion completed.")

if __name__ == "__main__":
    importer = PrologToGraph(prolog_dir="prolog_facts")
    try:
        importer.ingest_data()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        importer.close()