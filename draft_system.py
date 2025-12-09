"""
SISTEM REKOMENDASI DRAFT PICK MOBILE LEGENDS
Versi Python dari draft_system.pl
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import os


class Lane(str, Enum):
    GOLD = "gold"
    JUNGLE = "jungle"
    ROAM = "roam"
    MID = "mid"
    EXP = "exp"


class Role(str, Enum):
    TANK = "tank"
    FIGHTER = "fighter"
    ASSASSIN = "assassin"
    MAGE = "mage"
    MARKSMAN = "marksman"
    SUPPORT = "support"


class DamageType(str, Enum):
    PHYSICAL = "physical"
    MAGIC = "magic"
    TRUE = "true"


@dataclass
class HeroRecommendation:
    hero: str
    priority: float
    reasons: List[str]


@dataclass
class TeamAnalysis:
    role_counts: Dict[str, int]
    lane_counts: Dict[str, int]
    role_diversity: int
    missing_lanes: List[str]
    damage_balance: str
    jungle_roam_valid: str
    lane_validation: Dict


@dataclass
class DraftResult:
    recommendations: List[HeroRecommendation]
    team_analysis: Optional[TeamAnalysis]
    enemy_threats: Optional[List[Dict]]


class DraftSystem:
    """Sistem Draft Pick Mobile Legends"""
    
    def __init__(self):
        self.heroes: Set[str] = set()
        self.hero_roles: Dict[str, List[str]] = {}
        self.hero_lanes: Dict[str, List[str]] = {}
        self.hero_damage_types: Dict[str, List[str]] = {}
        self.counters: List[Tuple[str, str]] = []  # (hero1, hero2) = hero1 counter hero2
        self.compatible: List[Tuple[str, str]] = []  # (hero1, hero2) = compatible
        
        self._load_data()
    
    def _load_data(self):
        """Load data dari file prolog facts"""
        prolog_dir = "prolog_facts"
        
        # Load heroes
        self._load_heroes(os.path.join(prolog_dir, "hero.pl"))
        
        # Load roles
        self._load_roles(os.path.join(prolog_dir, "role.pl"))
        
        # Load lanes
        self._load_lanes(os.path.join(prolog_dir, "lane.pl"))
        
        # Load damage types
        self._load_damage_types(os.path.join(prolog_dir, "damage_type.pl"))
        
        # Load counters
        self._load_counters(os.path.join(prolog_dir, "counter.pl"))
        
        # Load compatible
        self._load_compatible(os.path.join(prolog_dir, "compatible.pl"))
    
    def _parse_prolog_fact(self, line: str, predicate: str) -> Optional[List[str]]:
        """Parse fakta prolog seperti: memiliki_role(hero, role)."""
        line = line.strip()
        if line.startswith(predicate + "(") and line.endswith(")."):
            # Extract arguments
            content = line[len(predicate)+1:-2]
            args = [arg.strip() for arg in content.split(",")]
            return args
        return None
    
    def _load_heroes(self, filepath: str):
        """Load daftar hero"""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                args = self._parse_prolog_fact(line, "hero")
                if args and len(args) == 1:
                    self.heroes.add(args[0])
    
    def _load_roles(self, filepath: str):
        """Load role setiap hero"""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                args = self._parse_prolog_fact(line, "memiliki_role")
                if args and len(args) == 2:
                    hero, role = args
                    if hero not in self.hero_roles:
                        self.hero_roles[hero] = []
                    self.hero_roles[hero].append(role)
    
    def _load_lanes(self, filepath: str):
        """Load lane setiap hero"""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                args = self._parse_prolog_fact(line, "memiliki_lane")
                if args and len(args) == 2:
                    hero, lane = args
                    if hero not in self.hero_lanes:
                        self.hero_lanes[hero] = []
                    self.hero_lanes[hero].append(lane)
    
    def _load_damage_types(self, filepath: str):
        """Load damage type setiap hero"""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                args = self._parse_prolog_fact(line, "memiliki_damage_type")
                if args and len(args) == 2:
                    hero, damage_type = args
                    if hero not in self.hero_damage_types:
                        self.hero_damage_types[hero] = []
                    self.hero_damage_types[hero].append(damage_type)
    
    def _load_counters(self, filepath: str):
        """Load counter relationships"""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                args = self._parse_prolog_fact(line, "iscounter")
                if args and len(args) == 2:
                    self.counters.append((args[0], args[1]))
    
    def _load_compatible(self, filepath: str):
        """Load compatible relationships"""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                args = self._parse_prolog_fact(line, "compatible")
                if args and len(args) == 2:
                    self.compatible.append((args[0], args[1]))
    
    # ===== UTILITY METHODS =====
    
    def extract_hero(self, hero_lane: str) -> str:
        """Extract hero dari format hero-lane"""
        if "-" in hero_lane:
            return hero_lane.split("-")[0]
        return hero_lane
    
    def extract_lane(self, hero_lane: str) -> Optional[str]:
        """Extract lane dari format hero-lane"""
        if "-" in hero_lane:
            return hero_lane.split("-")[1]
        return None
    
    def extract_all_heroes(self, team: List[str]) -> List[str]:
        """Extract semua hero dari list (dengan atau tanpa lane specification)"""
        return [self.extract_hero(hl) for hl in team]
    
    def hero_tersedia(self, hero: str, banned: List[str], enemy: List[str], team: List[str]) -> bool:
        """Cek apakah hero tidak dibanned dan tidak dipick"""
        if hero not in self.heroes:
            return False
        if hero in banned:
            return False
        if hero in enemy:
            return False
        team_heroes = self.extract_all_heroes(team)
        if hero in team_heroes:
            return False
        return True
    
    def memiliki_role(self, hero: str, role: str) -> bool:
        """Cek apakah hero memiliki role tertentu"""
        return hero in self.hero_roles and role in self.hero_roles[hero]
    
    def memiliki_lane(self, hero: str, lane: str) -> bool:
        """Cek apakah hero bisa main di lane tertentu"""
        return hero in self.hero_lanes and lane in self.hero_lanes[hero]
    
    def memiliki_damage_type(self, hero: str, damage_type: str) -> bool:
        """Cek apakah hero memiliki damage type tertentu"""
        return hero in self.hero_damage_types and damage_type in self.hero_damage_types[hero]
    
    def count_role_in_team(self, role: str, team: List[str]) -> int:
        """Hitung jumlah hero per role dalam tim"""
        count = 0
        for hero_lane in team:
            hero = self.extract_hero(hero_lane)
            if self.memiliki_role(hero, role):
                count += 1
        return count
    
    def count_specified_lane_in_team(self, lane: str, team: List[str]) -> int:
        """Hitung hero dengan spesifikasi lane yang jelas"""
        count = 0
        for hero_lane in team:
            if "-" in hero_lane:
                _, hero_lane_spec = hero_lane.split("-", 1)
                if hero_lane_spec == lane:
                    count += 1
        return count
    
    def lane_terpenuhi(self, lane: str, team: List[str]) -> bool:
        """Cek apakah lane sudah terpenuhi dalam tim"""
        return self.count_specified_lane_in_team(lane, team) > 0
    
    def lane_dibutuhkan(self, lane: str, team: List[str]) -> bool:
        """Cek apakah tim kekurangan lane tertentu"""
        return not self.lane_terpenuhi(lane, team)
    
    def count_unique_roles(self, team: List[str]) -> int:
        """Hitung jumlah role yang berbeda dalam tim"""
        roles = set()
        for hero_lane in team:
            hero = self.extract_hero(hero_lane)
            if hero in self.hero_roles:
                for role in self.hero_roles[hero]:
                    roles.add(role)
        return len(roles)
    
    def adds_role_diversity(self, hero: str, team: List[str]) -> bool:
        """Cek apakah hero menambah diversity role ke tim"""
        if hero not in self.hero_roles:
            return False
        
        hero_roles = self.hero_roles[hero]
        team_roles = set()
        for hero_lane in team:
            h = self.extract_hero(hero_lane)
            if h in self.hero_roles:
                team_roles.update(self.hero_roles[h])
        
        # Cek apakah ada role baru
        for role in hero_roles:
            if role not in team_roles:
                return True
        return False
    
    def would_duplicate_lane(self, hero: str, team: List[str], user_lane: str) -> bool:
        """Cek apakah hero akan menyebabkan duplikasi lane"""
        if not self.memiliki_lane(hero, user_lane):
            return False
        
        # Cek apakah ada hero yang sudah assigned ke lane ini
        for hero_lane in team:
            if "-" in hero_lane:
                _, lane = hero_lane.split("-", 1)
                if lane == user_lane:
                    return True
        return False
    
    def valid_lane_addition(self, hero: str, team: List[str], user_lane: str) -> bool:
        """Cek apakah penambahan hero valid (tidak duplikasi lane)"""
        return not self.would_duplicate_lane(hero, team, user_lane)
    
    def flexibility_score(self, hero: str) -> int:
        """Hitung skor fleksibilitas hero (berdasarkan jumlah role dan lane)"""
        role_count = len(self.hero_roles.get(hero, []))
        lane_count = len(self.hero_lanes.get(hero, []))
        return role_count + lane_count
    
    def is_counter_pick(self, hero: str, enemy_heroes: List[str]) -> bool:
        """Cek apakah hero adalah counter untuk musuh"""
        for enemy in enemy_heroes:
            if (hero, enemy) in self.counters:
                return True
        return False
    
    def good_synergy_with_team(self, hero: str, team: List[str]) -> bool:
        """Cek kompatibilitas dengan tim"""
        if not team:
            return False
        
        for hero_lane in team:
            teammate = self.extract_hero(hero_lane)
            if (hero, teammate) in self.compatible or (teammate, hero) in self.compatible:
                return True
        return False
    
    def has_damage_balance(self, team: List[str]) -> bool:
        """Cek keseimbangan damage type"""
        if len(team) <= 1:
            return True
        
        has_physical = False
        has_magic = False
        
        for hero_lane in team:
            hero = self.extract_hero(hero_lane)
            if self.memiliki_damage_type(hero, "physical"):
                has_physical = True
            if self.memiliki_damage_type(hero, "magic"):
                has_magic = True
        
        return has_physical and has_magic
    
    def get_jungle_hero(self, team: List[str]) -> Optional[str]:
        """Cek hero jungle dalam tim"""
        for hero_lane in team:
            if "-" in hero_lane:
                hero, lane = hero_lane.split("-", 1)
                if lane == "jungle":
                    return hero
        return None
    
    def get_roam_hero(self, team: List[str]) -> Optional[str]:
        """Cek hero roam dalam tim"""
        for hero_lane in team:
            if "-" in hero_lane:
                hero, lane = hero_lane.split("-", 1)
                if lane == "roam":
                    return hero
        return None
    
    def recommended_roam_role_for_jungle(self, jungle_hero: str) -> str:
        """Rekomendasi roam role berdasarkan jungle"""
        if self.memiliki_role(jungle_hero, "assassin"):
            return "tank"
        elif self.memiliki_role(jungle_hero, "tank") or self.memiliki_role(jungle_hero, "fighter"):
            return "support"
        return "tank"  # default
    
    def valid_jungle_roam_combination(self, team: List[str]) -> bool:
        """Cek apakah jungle-roam combination valid"""
        jungle_hero = self.get_jungle_hero(team)
        roam_hero = self.get_roam_hero(team)
        
        # Jika belum ada jungle atau roam, masih valid
        if not jungle_hero or not roam_hero:
            return True
        
        # Jika ada jungle assassin, roam harus tank
        if self.memiliki_role(jungle_hero, "assassin") and self.memiliki_role(roam_hero, "tank"):
            return True
        
        # Jika ada jungle tank/fighter, roam harus support
        if (self.memiliki_role(jungle_hero, "tank") or self.memiliki_role(jungle_hero, "fighter")) and \
           self.memiliki_role(roam_hero, "support"):
            return True
        
        return False
    
    # ===== PRIORITY CALCULATION =====
    
    def calculate_priority(self, hero: str, enemy_heroes: List[str], team_heroes: List[str], user_lane: str) -> Tuple[float, List[str]]:
        """Kalkulasi prioritas hero berdasarkan berbagai faktor"""
        reasons = []
        
        # Base priority
        priority = 10.0
        
        # Bonus untuk counter pick
        if self.is_counter_pick(hero, enemy_heroes):
            priority += 20
            reasons.append("Counter pick terhadap musuh")
        
        # Bonus untuk lane yang dibutuhkan tim (prioritas utama)
        lane_bonus = self._check_needed_lane_bonus(hero, team_heroes, user_lane)
        if lane_bonus > 0:
            priority += lane_bonus
            reasons.append(f"Mengisi lane yang dibutuhkan (+{lane_bonus})")
        
        # Bonus untuk role diversity
        role_bonus = self._check_role_diversity_bonus(hero, team_heroes)
        if role_bonus > 0:
            priority += role_bonus
            reasons.append(f"Menambah variasi role (+{role_bonus})")
        
        # Bonus untuk jungle-roam combination rules
        jr_bonus = self._check_jungle_roam_bonus(hero, team_heroes, user_lane)
        if jr_bonus > 0:
            priority += jr_bonus
            reasons.append(f"Kombinasi jungle-roam yang baik (+{jr_bonus})")
        
        # Bonus untuk synergy dengan tim
        if self.good_synergy_with_team(hero, team_heroes):
            priority += 10
            reasons.append("Synergy baik dengan tim (+10)")
        
        # Bonus untuk keseimbangan damage
        damage_bonus = self._check_damage_balance_bonus(hero, team_heroes)
        if damage_bonus > 0:
            priority += damage_bonus
            reasons.append(f"Menyeimbangkan damage type (+{damage_bonus})")
        
        # Bonus fleksibilitas
        flex_score = self.flexibility_score(hero)
        flex_bonus = flex_score * 2
        priority += flex_bonus
        reasons.append(f"Hero fleksibel (+{flex_bonus})")
        
        # Penalti untuk duplikasi lane (safety check)
        if self.would_duplicate_lane(hero, team_heroes, user_lane):
            priority -= 50
            reasons.append("WARNING: Duplikasi lane (-50)")
        
        return priority, reasons
    
    def _check_role_diversity_bonus(self, hero: str, team_heroes: List[str]) -> float:
        """Helper untuk bonus role diversity"""
        current_diversity = self.count_unique_roles(team_heroes)
        if self.adds_role_diversity(hero, team_heroes):
            bonus = 20 - (current_diversity * 3)
            return max(0, bonus)
        return 0
    
    def _check_needed_lane_bonus(self, hero: str, team_heroes: List[str], user_lane: str) -> float:
        """Helper untuk bonus lane yang dibutuhkan"""
        if self.memiliki_lane(hero, user_lane) and self.lane_dibutuhkan(user_lane, team_heroes):
            return 25
        
        # Cek lane lain yang dibutuhkan
        for lane in ["gold", "jungle", "roam", "mid", "exp"]:
            if self.memiliki_lane(hero, lane) and self.lane_dibutuhkan(lane, team_heroes):
                return 20
        
        return 0
    
    def _check_jungle_roam_bonus(self, hero: str, team_heroes: List[str], user_lane: str) -> float:
        """Helper untuk bonus jungle-roam combination"""
        # Jika user pick roam
        if user_lane == "roam":
            jungle_hero = self.get_jungle_hero(team_heroes)
            if jungle_hero:
                recommended_role = self.recommended_roam_role_for_jungle(jungle_hero)
                if self.memiliki_role(hero, recommended_role):
                    return 15
        
        # Jika user pick jungle
        if user_lane == "jungle":
            roam_hero = self.get_roam_hero(team_heroes)
            if roam_hero:
                # Cek apakah hero jungle cocok dengan roam yang sudah ada
                if self.memiliki_role(roam_hero, "tank") and self.memiliki_role(hero, "assassin"):
                    return 15
                if self.memiliki_role(roam_hero, "support") and \
                   (self.memiliki_role(hero, "tank") or self.memiliki_role(hero, "fighter")):
                    return 15
        
        return 0
    
    def _check_damage_balance_bonus(self, hero: str, team_heroes: List[str]) -> float:
        """Helper untuk bonus keseimbangan damage"""
        has_magic = False
        has_physical = False
        
        for hero_lane in team_heroes:
            h = self.extract_hero(hero_lane)
            if self.memiliki_damage_type(h, "magic"):
                has_magic = True
            if self.memiliki_damage_type(h, "physical"):
                has_physical = True
        
        # Jika tim kekurangan magic damage dan hero adalah mage
        if not has_magic and self.memiliki_damage_type(hero, "magic"):
            return 8
        
        # Jika tim kekurangan physical damage dan hero adalah physical
        if not has_physical and self.memiliki_damage_type(hero, "physical"):
            return 8
        
        return 0
    
    # ===== MAIN RECOMMENDATION METHODS =====
    
    def recommend_first_pick(self, banned: List[str], user_lane: str, top_n: int = 5) -> List[HeroRecommendation]:
        """Rekomendasi untuk first pick - prioritas hero fleksibel"""
        recommendations = []
        
        for hero in self.heroes:
            if not self.hero_tersedia(hero, banned, [], []):
                continue
            
            if not self.memiliki_lane(hero, user_lane):
                continue
            
            flex_score = self.flexibility_score(hero)
            if flex_score < 3:  # Hero dengan minimal 3 poin fleksibilitas
                continue
            
            # Pastikan hero memiliki sedikit counter yang diketahui
            counter_count = sum(1 for c, _ in self.counters if c == hero)
            if counter_count > 2:
                continue
            
            recommendations.append(HeroRecommendation(
                hero=hero,
                priority=float(flex_score),
                reasons=[f"Hero fleksibel (score: {flex_score})"]
            ))
        
        # Sort by priority descending
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        return recommendations[:top_n]
    
    def recommend_hero(self, banned: List[str], enemy: List[str], team: List[str], 
                      user_lane: str, top_n: int = 5) -> List[HeroRecommendation]:
        """Rekomendasi hero berdasarkan situasi draft"""
        recommendations = []
        
        for hero in self.heroes:
            if not self.hero_tersedia(hero, banned, enemy, team):
                continue
            
            if not self.memiliki_lane(hero, user_lane):
                continue
            
            if not self.valid_lane_addition(hero, team, user_lane):
                continue
            
            priority, reasons = self.calculate_priority(hero, enemy, team, user_lane)
            
            recommendations.append(HeroRecommendation(
                hero=hero,
                priority=priority,
                reasons=reasons
            ))
        
        # Sort by priority descending
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        return recommendations[:top_n]
    
    def analyze_team_composition(self, team: List[str]) -> TeamAnalysis:
        """Analisis komposisi tim saat ini"""
        # Role counts
        role_counts = {}
        for role in ["tank", "fighter", "assassin", "mage", "marksman", "support"]:
            role_counts[role] = self.count_role_in_team(role, team)
        
        # Lane counts
        lane_counts = {}
        for lane in ["gold", "jungle", "roam", "mid", "exp"]:
            lane_counts[lane] = self.count_specified_lane_in_team(lane, team)
        
        # Role diversity
        role_diversity = self.count_unique_roles(team)
        
        # Missing lanes
        missing_lanes = []
        for lane in ["gold", "jungle", "roam", "mid", "exp"]:
            if self.lane_dibutuhkan(lane, team):
                missing_lanes.append(lane)
        
        # Damage balance
        damage_balance = "balanced" if self.has_damage_balance(team) else "unbalanced"
        
        # Jungle-roam validation
        jungle_roam_valid = "valid" if self.valid_jungle_roam_combination(team) else "invalid"
        
        # Lane validation
        lane_validation = {
            "valid": len(missing_lanes) == 0,
            "missing_lanes": missing_lanes
        }
        
        return TeamAnalysis(
            role_counts=role_counts,
            lane_counts=lane_counts,
            role_diversity=role_diversity,
            missing_lanes=missing_lanes,
            damage_balance=damage_balance,
            jungle_roam_valid=jungle_roam_valid,
            lane_validation=lane_validation
        )
    
    def analyze_enemy_threats(self, enemy_heroes: List[str]) -> List[Dict]:
        """Analisis threat dari tim musuh"""
        threats = []
        for enemy in enemy_heroes:
            counters = [hero for hero, target in self.counters if target == enemy]
            threats.append({
                "enemy": enemy,
                "counters": counters
            })
        return threats
    
    def get_draft_recommendation(self, banned: List[str], enemy: List[str], 
                                team: List[str], user_lane: str) -> DraftResult:
        """Interface utama sistem draft"""
        # Cek apakah ini first pick
        if not enemy and not team:
            recommendations = self.recommend_first_pick(banned, user_lane)
            return DraftResult(
                recommendations=recommendations,
                team_analysis=None,
                enemy_threats=None
            )
        else:
            recommendations = self.recommend_hero(banned, enemy, team, user_lane)
            team_analysis = self.analyze_team_composition(team)
            enemy_threats = self.analyze_enemy_threats(enemy)
            return DraftResult(
                recommendations=recommendations,
                team_analysis=team_analysis,
                enemy_threats=enemy_threats
            )


# ===== TESTING =====
if __name__ == "__main__":
    # Initialize system
    print("🚀 Initializing Draft System...")
    draft = DraftSystem()
    print(f"✅ Loaded {len(draft.heroes)} heroes")
    print(f"✅ Loaded {len(draft.counters)} counter relationships")
    print(f"✅ Loaded {len(draft.compatible)} compatible relationships")
    
    # Test 1: First Pick
    print("\n" + "="*60)
    print("TEST 1: First Pick untuk lane Gold")
    print("="*60)
    result = draft.get_draft_recommendation([], [], [], "gold")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"{i}. {rec.hero.upper()} (Score: {rec.priority:.1f})")
        for reason in rec.reasons:
            print(f"   - {reason}")
    
    # Test 2: Counter Pick
    print("\n" + "="*60)
    print("TEST 2: Counter Pick (Enemy: fanny, gusion | Team: angela-roam)")
    print("="*60)
    result = draft.get_draft_recommendation(
        banned=[],
        enemy=["fanny", "gusion"],
        team=["angela-roam"],
        user_lane="mid"
    )
    for i, rec in enumerate(result.recommendations, 1):
        print(f"{i}. {rec.hero.upper()} (Priority: {rec.priority:.1f})")
        for reason in rec.reasons:
            print(f"   - {reason}")
    
    # Test 3: Melengkapi tim
    print("\n" + "="*60)
    print("TEST 3: Melengkapi Tim (Banned: johnson, akai | Enemy: hayabusa, eudora, layla | Team: tigreal-roam, harith-mid)")
    print("="*60)
    result = draft.get_draft_recommendation(
        banned=["johnson", "akai"],
        enemy=["hayabusa", "eudora", "layla"],
        team=["tigreal-roam", "harith-mid"],
        user_lane="jungle"
    )
    for i, rec in enumerate(result.recommendations, 1):
        print(f"{i}. {rec.hero.upper()} (Priority: {rec.priority:.1f})")
        for reason in rec.reasons:
            print(f"   - {reason}")
    
    if result.team_analysis:
        print("\n📊 Team Analysis:")
        print(f"   Role Diversity: {result.team_analysis.role_diversity}")
        print(f"   Missing Lanes: {result.team_analysis.missing_lanes}")
        print(f"   Damage Balance: {result.team_analysis.damage_balance}")
        print(f"   Jungle-Roam: {result.team_analysis.jungle_roam_valid}")
