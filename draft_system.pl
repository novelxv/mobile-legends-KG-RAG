% ===== SISTEM REKOMENDASI DRAFT PICK MOBILE LEGENDS =====

% Include semua fakta yang diperlukan
:- include('prolog_facts/hero.pl').
:- include('prolog_facts/role.pl').
:- include('prolog_facts/lane.pl').
:- include('prolog_facts/damage_type.pl').
:- include('prolog_facts/specialty.pl').
:- include('prolog_facts/compatible.pl').
:- include('prolog_facts/counter.pl').

% ===== UTILITY PREDICATES =====

% Cek apakah hero tidak dibanned dan tidak dipick tim/musuh
hero_tersedia(Hero, BannedHeroes, EnemyHeroes, TeamHeroes) :-
    hero(Hero),
    \+ member(Hero, BannedHeroes),
    \+ member(Hero, EnemyHeroes),
    extract_all_heroes(TeamHeroes, TeamHeroList),
    \+ member(Hero, TeamHeroList).

% Hitung jumlah hero per role dalam tim
count_role_in_team(Role, Team, Count) :-
    count_role_in_team_v2(Role, Team, Count).

% Hitung jumlah hero per lane dalam tim
count_lane_in_team(Lane, Team, Count) :-
    count_specified_lane_in_team(Lane, Team, Count).

% Cek apakah lane sudah terpenuhi dalam tim (minimal 1)
lane_terpenuhi(Lane, Team) :-
    count_specified_lane_in_team(Lane, Team, Count),
    Count > 0.

% Cek apakah tim kekurangan lane tertentu
lane_dibutuhkan(Lane, Team) :-
    lane(Lane),
    \+ lane_terpenuhi(Lane, Team).

% Hitung jumlah role yang berbeda dalam tim
count_unique_roles(Team, UniqueRoleCount) :-
    findall(Role, (
        member(HeroLane, Team),
        extract_hero(HeroLane, Hero),
        memiliki_role(Hero, Role)
    ), AllRoles),
    sort(AllRoles, UniqueRoles),
    length(UniqueRoles, UniqueRoleCount).

% Cek apakah hero menambah diversity role ke tim
adds_role_diversity(Hero, Team) :-
    memiliki_role(Hero, Role),
    \+ (member(TeamMateLane, Team), 
        extract_hero(TeamMateLane, TeamMate),
        memiliki_role(TeamMate, Role)).

% ===== HERO-LANE FORMAT UTILITIES =====

% Extract hero dari format hero-lane
extract_hero(Hero-_Lane, Hero) :- !.
extract_hero(Hero, Hero).

% Extract lane dari format hero-lane
extract_lane(Hero-Lane, Hero, Lane) :- !.
extract_lane(Hero, Hero, _) :- 
    % Jika tidak ada spesifikasi lane, kita tidak bisa tentukan
    fail.

% Extract semua hero dari list (dengan atau tanpa lane specification)
extract_all_heroes([], []).
extract_all_heroes([HeroLane|Rest], [Hero|HeroRest]) :-
    extract_hero(HeroLane, Hero),
    extract_all_heroes(Rest, HeroRest).

% Cek apakah hero sudah dipick dengan spesifikasi lane
hero_already_picked_in_lane(Hero, Lane, Team) :-
    member(Hero-Lane, Team), !.
hero_already_picked_in_lane(Hero, _Lane, Team) :-
    member(Hero, Team).

% Update count functions untuk hero-lane format
count_role_in_team_v2(Role, Team, Count) :-
    findall(Hero, (
        member(HeroLane, Team),
        extract_hero(HeroLane, Hero),
        memiliki_role(Hero, Role)
    ), RoleHeroes),
    length(RoleHeroes, Count).

% Count lane dengan spesifikasi yang tepat
count_specified_lane_in_team(Lane, Team, Count) :-
    findall(Hero, (
        member(Hero-SpecifiedLane, Team),
        SpecifiedLane = Lane
    ), LaneHeroes),
    length(LaneHeroes, Count).

% Fallback untuk hero tanpa spesifikasi lane
count_lane_in_team_v2(Lane, Team, Count) :-
    % Hitung hero dengan spesifikasi lane yang jelas
    count_specified_lane_in_team(Lane, Team, SpecifiedCount),
    % Hitung hero tanpa spesifikasi yang bisa main di lane ini
    findall(Hero, (
        member(Hero, Team),
        \+ (member(Hero-_, Team)), % Hero tanpa spesifikasi lane
        memiliki_lane(Hero, Lane)
    ), UnspecifiedHeroes),
    length(UnspecifiedHeroes, UnspecifiedCount),
    Count is SpecifiedCount + UnspecifiedCount.

% Cek apakah hero akan menyebabkan duplikasi lane
would_duplicate_lane(Hero, Team, UserLane) :-
    memiliki_lane(Hero, UserLane),
    % Cek apakah ada hero yang sudah assigned ke lane ini
    member(_TeamMate-UserLane, Team).
    
would_duplicate_lane_old(Hero, Team, UserLane) :-
    memiliki_lane(Hero, UserLane),
    member(TeamMate, Team),
    \+ (member(TeamMate-_, Team)), % Hero tanpa spesifikasi lane
    memiliki_lane(TeamMate, UserLane).

% Cek apakah penambahan hero valid (tidak duplikasi lane)
valid_lane_addition(Hero, Team, UserLane) :-
    \+ would_duplicate_lane(Hero, Team, UserLane).

% Hitung jumlah hero yang sudah mengisi lane tertentu
count_heroes_in_lane(Lane, Team, Count) :-
    % Prioritas: hitung hero dengan spesifikasi lane yang jelas
    count_specified_lane_in_team(Lane, Team, Count).

% Validasi apakah hero bisa main di lane yang dispesifikasi
valid_hero_lane_assignment(Hero, Lane) :-
    memiliki_lane(Hero, Lane).

% Cek hero yang tidak sesuai dengan lane assignment
check_invalid_lane_assignments(Team, InvalidAssignments) :-
    findall(
        Hero-Lane,
        (
            member(Hero-Lane, Team),
            \+ valid_hero_lane_assignment(Hero, Lane)
        ),
        InvalidAssignments
    ).

% Comprehensive lane validation
comprehensive_lane_validation(Team, ValidationResult) :-
    % Cek duplikasi
    findall(Lane, (lane(Lane), count_heroes_in_lane(Lane, Team, Count), Count > 1), DuplicatedLanes),
    
    % Cek invalid assignments
    check_invalid_lane_assignments(Team, InvalidAssignments),
    
    % Tentukan status validasi
    (
        DuplicatedLanes = [], InvalidAssignments = [] ->
        ValidationResult = lane_validation(valid, [], [])
    ;
        ValidationResult = lane_validation(invalid, DuplicatedLanes, InvalidAssignments)
    ).

% Hitung skor fleksibilitas hero (berdasarkan jumlah role dan lane)
flexibility_score(Hero, FlexScore) :-
    hero(Hero),
    findall(Role, memiliki_role(Hero, Role), Roles),
    findall(Lane, memiliki_lane(Hero, Lane), Lanes),
    length(Roles, RoleCount),
    length(Lanes, LaneCount),
    FlexScore is RoleCount + LaneCount.

% Cek apakah hero adalah counter untuk musuh
is_counter_pick(Hero, EnemyHeroes) :-
    member(Enemy, EnemyHeroes),
    iscounter(Hero, Enemy).

% Cek kompatibilitas dengan tim
good_synergy_with_team(Hero, Team) :-
    Team \= [],
    member(TeamMateLane, Team),
    extract_hero(TeamMateLane, TeamMate),
    compatible(Hero, TeamMate).

% Cek keseimbangan damage type
has_damage_balance(Team) :-
    length(Team, Len),
    Len =< 1,
    !.
has_damage_balance(Team) :-
    member(HeroLane1, Team),
    extract_hero(HeroLane1, H1),
    memiliki_damage_type(H1, physical),
    member(HeroLane2, Team),
    extract_hero(HeroLane2, H2), 
    memiliki_damage_type(H2, magic).

% Cek hero jungle dalam tim
get_jungle_hero(Team, JungleHero) :-
    member(JungleHero-jungle, Team), !.
get_jungle_hero(Team, JungleHero) :-
    member(JungleHero, Team),
    \+ (member(JungleHero-_, Team)), % Hero tanpa spesifikasi lane
    memiliki_lane(JungleHero, jungle).

% Cek hero roam dalam tim
get_roam_hero(Team, RoamHero) :-
    member(RoamHero-roam, Team), !.
get_roam_hero(Team, RoamHero) :-
    member(RoamHero, Team),
    \+ (member(RoamHero-_, Team)),
    memiliki_lane(RoamHero, roam).

% Rules: Kalau jungle assassin, roam tank
jungle_roam_rule_assassin_tank(Team) :-
    get_jungle_hero(Team, JungleHero),
    memiliki_role(JungleHero, assassin),
    get_roam_hero(Team, RoamHero),
    memiliki_role(RoamHero, tank).

% Rules: Kalau jungle tank/fighter, roam support
jungle_roam_rule_tank_support(Team) :-
    get_jungle_hero(Team, JungleHero),
    (memiliki_role(JungleHero, tank) ; memiliki_role(JungleHero, fighter)),
    get_roam_hero(Team, RoamHero),
    memiliki_role(RoamHero, support).

% Cek apakah jungle-roam combination valid
valid_jungle_roam_combination(Team) :-
    % Jika belum ada jungle atau roam, masih valid
    (\+ get_jungle_hero(Team, _) ; \+ get_roam_hero(Team, _)),
    !.
valid_jungle_roam_combination(Team) :-
    % Jika ada jungle assassin, roam tank
    get_jungle_hero(Team, JungleHero),
    memiliki_role(JungleHero, assassin),
    get_roam_hero(Team, RoamHero),
    memiliki_role(RoamHero, tank),
    !.
valid_jungle_roam_combination(Team) :-
    % Jika ada jungle tank/fighter, roam support
    get_jungle_hero(Team, JungleHero),
    (memiliki_role(JungleHero, tank) ; memiliki_role(JungleHero, fighter)),
    get_roam_hero(Team, RoamHero),
    memiliki_role(RoamHero, support),
    !.

% Cek recommended roam role berdasarkan jungle
recommended_roam_role_for_jungle(JungleHero, RecommendedRoamRole) :-
    (memiliki_role(JungleHero, assassin) ->
        RecommendedRoamRole = tank
    ;
        (memiliki_role(JungleHero, tank) ; memiliki_role(JungleHero, fighter)) ->
        RecommendedRoamRole = support
    ;
        RecommendedRoamRole = tank  % default
    ).

% ===== ATURAN DRAFT PICK UTAMA =====

% Rule untuk First Pick - prioritas hero fleksibel
recommend_first_pick(Hero, BannedHeroes, EnemyHeroes, TeamHeroes, UserLane) :-
    hero_tersedia(Hero, BannedHeroes, EnemyHeroes, TeamHeroes),
    memiliki_lane(Hero, UserLane),
    flexibility_score(Hero, FlexScore),
    FlexScore >= 3,  % Hero dengan minimal 3 poin fleksibilitas
    % Pastikan hero memiliki sedikit counter yang diketahui
    \+ (findall(Counter, iscounter(Counter, Hero), Counters), 
        length(Counters, CounterCount), 
        CounterCount > 2).

% Rule utama untuk rekomendasi hero
recommend_hero(Hero, BannedHeroes, EnemyHeroes, TeamHeroes, UserLane, Priority) :-
    hero_tersedia(Hero, BannedHeroes, EnemyHeroes, TeamHeroes),
    memiliki_lane(Hero, UserLane),
    valid_lane_addition(Hero, TeamHeroes, UserLane),  % Validasi anti-duplikasi lane
    calculate_priority(Hero, EnemyHeroes, TeamHeroes, UserLane, Priority).

% Kalkulasi prioritas hero berdasarkan berbagai faktor
calculate_priority(Hero, EnemyHeroes, TeamHeroes, UserLane, Priority) :-
    % Base priority
    BasePriority = 10,
    
    % Bonus untuk counter pick
    (is_counter_pick(Hero, EnemyHeroes) -> CounterBonus = 20; CounterBonus = 0),
    
    % Bonus untuk lane yang dibutuhkan tim (prioritas utama)
    (check_needed_lane_bonus(Hero, TeamHeroes, UserLane, LaneBonus) -> true; LaneBonus = 0),
    
    % Bonus untuk role diversity
    (check_role_diversity_bonus(Hero, TeamHeroes, RoleDiversityBonus) -> true; RoleDiversityBonus = 0),
    
    % Bonus untuk jungle-roam combination rules
    (check_jungle_roam_bonus(Hero, TeamHeroes, UserLane, JungleRoamBonus) -> true; JungleRoamBonus = 0),
    
    % Bonus untuk synergy dengan tim
    (good_synergy_with_team(Hero, TeamHeroes) -> SynergyBonus = 10; SynergyBonus = 0),
    
    % Bonus untuk keseimbangan damage
    (check_damage_balance_bonus(Hero, TeamHeroes, DamageBonus) -> true; DamageBonus = 0),
    
    % Bonus fleksibilitas
    flexibility_score(Hero, FlexScore),
    FlexibilityBonus is FlexScore * 2,
    
    % Penalti untuk duplikasi lane (safety check)
    (would_duplicate_lane(Hero, TeamHeroes, UserLane) -> DuplicationPenalty = -50; DuplicationPenalty = 0),
    
    % Total priority
    Priority is BasePriority + CounterBonus + LaneBonus + RoleDiversityBonus + JungleRoamBonus + SynergyBonus + DamageBonus + FlexibilityBonus + DuplicationPenalty.

% Helper untuk bonus role diversity
check_role_diversity_bonus(Hero, TeamHeroes, Bonus) :-
    count_unique_roles(TeamHeroes, CurrentDiversity),
    (adds_role_diversity(Hero, TeamHeroes) ->
        % Bonus berdasarkan seberapa diverse tim saat ini
        % Semakin sedikit diversity, semakin besar bonus untuk menambah role baru
        Bonus is 20 - (CurrentDiversity * 3)
    ;
        Bonus = 0
    ),
    Bonus >= 0.  % Minimal 0, tidak negatif

% Helper untuk bonus lane yang dibutuhkan (prioritas utama)
check_needed_lane_bonus(Hero, TeamHeroes, UserLane, 25) :-
    memiliki_lane(Hero, UserLane),
    lane_dibutuhkan(UserLane, TeamHeroes),
    !.
check_needed_lane_bonus(Hero, TeamHeroes, _, 20) :-
    memiliki_lane(Hero, Lane),
    lane_dibutuhkan(Lane, TeamHeroes),
    !.
check_needed_lane_bonus(_, _, _, 0).

% Helper untuk bonus jungle-roam combination
check_jungle_roam_bonus(Hero, TeamHeroes, UserLane, 15) :-
    UserLane = roam,
    get_jungle_hero(TeamHeroes, JungleHero),
    recommended_roam_role_for_jungle(JungleHero, RecommendedRole),
    memiliki_role(Hero, RecommendedRole),
    !.
check_jungle_roam_bonus(Hero, TeamHeroes, UserLane, 15) :-
    UserLane = jungle,
    get_roam_hero(TeamHeroes, RoamHero),
    % Cek apakah hero jungle cocok dengan roam yang sudah ada
    ((memiliki_role(RoamHero, tank), memiliki_role(Hero, assassin)) ;
     (memiliki_role(RoamHero, support), (memiliki_role(Hero, tank) ; memiliki_role(Hero, fighter)))),
    !.
check_jungle_roam_bonus(_, _, _, 0).

% Helper untuk bonus keseimbangan damage
check_damage_balance_bonus(Hero, TeamHeroes, 8) :-
    % Jika tim kekurangan magic damage dan hero adalah mage
    \+ ( member(TeamMateLane, TeamHeroes),
         extract_hero(TeamMateLane, TeamMate),
         memiliki_damage_type(TeamMate, magic)
       ),
    memiliki_damage_type(Hero, magic),
    !.
check_damage_balance_bonus(Hero, TeamHeroes, 8) :-
    % Jika tim kekurangan physical damage dan hero adalah physical
    \+ ( member(TeamMateLane, TeamHeroes),
         extract_hero(TeamMateLane, TeamMate),
         memiliki_damage_type(TeamMate, physical)
       ),
    memiliki_damage_type(Hero, physical),
    !.
check_damage_balance_bonus(_, _, 0).

% ===== MAIN SYSTEM PREDICATES =====

% Sistem utama untuk first pick
get_first_pick_recommendations(BannedHeroes, UserLane, Recommendations) :-
    EnemyHeroes = [],
    TeamHeroes = [],
    findall(
        hero_priority(Hero, Score),
        (recommend_first_pick(Hero, BannedHeroes, EnemyHeroes, TeamHeroes, UserLane),
         flexibility_score(Hero, Score)),
        UnsortedRecs
    ),
    sort(2, @>=, UnsortedRecs, SortedRecs),  % Sort by score descending
    take_top_n(SortedRecs, 5, Recommendations).

% Sistem utama untuk rekomendasi hero
get_hero_recommendations(BannedHeroes, EnemyHeroes, TeamHeroes, UserLane, Recommendations) :-
    findall(
        hero_priority(Hero, Priority),
        recommend_hero(Hero, BannedHeroes, EnemyHeroes, TeamHeroes, UserLane, Priority),
        UnsortedRecs
    ),
    sort(2, @>=, UnsortedRecs, SortedRecs),  % Sort by priority descending
    take_top_n(SortedRecs, 5, Recommendations).

% Helper untuk mengambil top N recommendations
take_top_n(List, N, TopN) :-
    length(List, Len),
    (Len > N -> 
        length(TopN, N), 
        append(TopN, _, List)
    ; 
        TopN = List
    ).

% ===== ANALYSIS PREDICATES =====

% Analisis komposisi tim saat ini
analyze_team_composition(Team, Analysis) :-
    findall(Role-Count, (role(Role), count_role_in_team_v2(Role, Team, Count)), RoleCounts),
    findall(Lane-Count, (lane(Lane), count_specified_lane_in_team(Lane, Team, Count)), LaneCounts),
    count_unique_roles(Team, RoleDiversity),
    findall(Lane, (lane(Lane), lane_dibutuhkan(Lane, Team)), MissingLanes),
    (has_damage_balance(Team) -> DamageBalance = balanced; DamageBalance = unbalanced),
    (valid_jungle_roam_combination(Team) -> JungleRoamValid = valid; JungleRoamValid = invalid),
    comprehensive_lane_validation(Team, LaneValidationResult),
    Analysis = team_analysis(RoleCounts, LaneCounts, RoleDiversity, MissingLanes, DamageBalance, JungleRoamValid, LaneValidationResult).

% Analisis threat dari tim musuh
analyze_enemy_threats(EnemyHeroes, Threats) :-
    findall(
        threat(Enemy, Counters),
        (member(Enemy, EnemyHeroes),
         findall(Counter, iscounter(Counter, Enemy), Counters)),
        Threats
    ).

% ===== INTERFACE PREDICATES =====

% Interface utama sistem
draft_recommendation(BannedHeroes, EnemyHeroes, TeamHeroes, UserLane, Result) :-
    % Cek apakah ini first pick
    (EnemyHeroes = [], TeamHeroes = [] ->
        get_first_pick_recommendations(BannedHeroes, UserLane, Recommendations),
        Result = first_pick_recommendations(Recommendations)
    ;
        get_hero_recommendations(BannedHeroes, EnemyHeroes, TeamHeroes, UserLane, Recommendations),
        analyze_team_composition(TeamHeroes, TeamAnalysis),
        analyze_enemy_threats(EnemyHeroes, EnemyThreats),
        Result = draft_analysis(Recommendations, TeamAnalysis, EnemyThreats)
    ).

% ===== CONTOH QUERY =====
/*
Contoh penggunaan:

Format:
draft_recommendation(BannedList, EnemyList, TeamList, UserLane, Result).

1. First Pick:
?- draft_recommendation([], [], [], gold, Result).

2. Counter Pick:
?- draft_recommendation([], [fanny, gusion], [angela], mid, Result).

3. Melengkapi tim:
?- draft_recommendation([johnson, akai], [hayabusa, eudora, layla], [tigreal, harith], jungle, Result).
*/