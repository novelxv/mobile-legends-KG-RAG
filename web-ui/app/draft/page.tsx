'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
}

interface Hero {
  name: string;
  roles: string[];
  lanes: string[];
  damage_types: string[];
}

interface Recommendation {
  hero: string;
  priority: number;
  reasons: string[];
}

interface TeamAnalysis {
  role_counts: Record<string, number>;
  lane_counts: Record<string, number>;
  role_diversity: number;
  missing_lanes: string[];
  damage_balance: string;
  jungle_roam_valid: string;
  lane_validation: {
    valid: boolean;
    missing_lanes: string[];
  };
}

interface DraftResponse {
  recommendations: Recommendation[];
  team_analysis?: TeamAnalysis;
  enemy_threats?: Array<{ enemy: string; counters: string[] }>;
  success: boolean;
  error?: string;
}

const LANES = ['gold', 'jungle', 'roam', 'mid', 'exp'];
const LANE_COLORS = {
  gold: 'bg-yellow-500',
  jungle: 'bg-green-500',
  roam: 'bg-blue-500',
  mid: 'bg-purple-500',
  exp: 'bg-red-500',
};

const LANE_LABELS = {
  gold: 'Gold',
  jungle: 'Jungle',
  roam: 'Roam',
  mid: 'Mid',
  exp: 'Exp',
};

export default function DraftPage() {
  const [heroes, setHeroes] = useState<Hero[]>([]);
  const [banned, setBanned] = useState<string[]>([]);
  const [enemy, setEnemy] = useState<string[]>([]);
  const [team, setTeam] = useState<string[]>([]);
  const [userLane, setUserLane] = useState<string>('gold');
  const [teamLaneInput, setTeamLaneInput] = useState<string>('gold');
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [teamAnalysis, setTeamAnalysis] = useState<TeamAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'banned' | 'enemy' | 'team'>('banned');
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    fetchHeroes();
  }, []);

  const showToast = (message: string, type: Toast['type'] = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 3000);
  };

  const fetchHeroes = async () => {
    try {
      const response = await axios.get('http://localhost:8000/draft/heroes');
      setHeroes(response.data.heroes);
    } catch (error) {
      console.error('Failed to fetch heroes:', error);
    }
  };

  const getDraftRecommendations = async () => {
    setLoading(true);
    try {
      const response = await axios.post<DraftResponse>('http://localhost:8000/draft', {
        banned,
        enemy,
        team,
        user_lane: userLane,
      });

      if (response.data.success) {
        setRecommendations(response.data.recommendations);
        setTeamAnalysis(response.data.team_analysis || null);
        showToast('Recommendations loaded successfully!', 'success');
      }
    } catch (error: any) {
      console.error('Failed to get recommendations:', error);
      showToast(error.response?.data?.detail || 'Failed to get recommendations', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleTeamInput = (input: string) => {
    const parts = input.toLowerCase().split(' ').filter(p => p);
    if (parts.length !== 2) {
      showToast('Format salah! Gunakan: hero lane (contoh: miya gold)', 'warning');
      return;
    }

    const [heroName, lane] = parts;
    
    // Validate lane
    if (!LANES.includes(lane)) {
      showToast(`Lane tidak valid! Gunakan: ${LANES.join(', ')}`, 'warning');
      return;
    }

    // Check if hero exists
    const heroExists = heroes.some(h => h.name.toLowerCase() === heroName);
    if (!heroExists) {
      showToast('Hero tidak ditemukan!', 'error');
      return;
    }

    // Check if hero is already in any list
    if (banned.includes(heroName) || enemy.includes(heroName) || team.some(h => h.startsWith(heroName))) {
      showToast('Hero sudah dipilih!', 'warning');
      return;
    }

    // Check if lane is already taken
    const laneExists = team.some(h => h.endsWith(`-${lane}`));
    if (laneExists) {
      showToast(`Lane ${lane} sudah ada! Pilih lane lain.`, 'warning');
      return;
    }

    // Add to team
    setTeam([...team, `${heroName}-${lane}`]);
    setSearchQuery('');
  };

  const addHeroWithLane = (heroName: string, lane: string) => {
    // Check if hero is already in any list
    if (banned.includes(heroName) || enemy.includes(heroName) || team.some(h => h.startsWith(heroName))) {
      showToast('Hero sudah dipilih!', 'warning');
      return;
    }

    // Check if lane is already taken
    const laneExists = team.some(h => h.endsWith(`-${lane}`));
    if (laneExists) {
      showToast(`Lane ${lane} sudah ada! Pilih lane lain.`, 'warning');
      return;
    }

    // Add to team
    setTeam([...team, `${heroName}-${lane}`]);
    setSearchQuery('');
    showToast(`${heroName} added to team as ${lane}!`, 'success');
  };

  const addHeroToList = (heroName: string, listType: 'banned' | 'enemy' | 'team') => {
    const lists = { banned, enemy, team };
    const setters = { banned: setBanned, enemy: setEnemy, team: setTeam };

    // Check if hero is already in any list
    if (banned.includes(heroName) || enemy.includes(heroName) || team.some(h => h.startsWith(heroName))) {
      showToast('Hero already selected!', 'warning');
      return;
    }

    if (listType === 'team') {
      showToast('Untuk team, ketik: hero lane (contoh: miya gold)', 'info');
      return;
    } else {
      setters[listType]([...lists[listType], heroName]);
      const listNames = { banned: 'banned', enemy: 'enemy' };
      showToast(`${heroName} added to ${listNames[listType]} list!`, 'success');
    }

    setSearchQuery('');
  };

  const removeHeroFromList = (heroName: string, listType: 'banned' | 'enemy' | 'team') => {
    if (listType === 'team') {
      setTeam(team.filter(h => !h.startsWith(heroName)));
    } else if (listType === 'banned') {
      setBanned(banned.filter(h => h !== heroName));
    } else {
      setEnemy(enemy.filter(h => h !== heroName));
    }
  };

  const resetDraft = () => {
    setBanned([]);
    setEnemy([]);
    setTeam([]);
    setRecommendations([]);
    setTeamAnalysis(null);
  };

  const filteredHeroes = heroes.filter(hero =>
    hero.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
    !banned.includes(hero.name) &&
    !enemy.includes(hero.name) &&
    !team.some(h => h.startsWith(hero.name))
  );

  const getHeroLane = (heroWithLane: string): string => {
    const parts = heroWithLane.split('-');
    return parts.length > 1 ? parts[1] : '';
  };

  return (
    <div className="min-h-screen relative">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-ml-blue/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-ml-accent/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Header */}
      <header className="relative border-b-2 border-ml-accent/30 backdrop-blur-md bg-ml-primary/50 shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-r from-ml-blue/10 via-transparent to-ml-accent/10"></div>
        <div className="container mx-auto px-6 py-6 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-ml-accent via-yellow-500 to-ml-orange 
                            flex items-center justify-center shadow-ml animate-glow overflow-hidden">
                <img src="/mobile-legends-logo.png" alt="Mobile Legends Logo" className="w-full h-full object-cover" />
              </div>
              <div>
                <h1 className="text-4xl md:text-5xl font-heading font-bold glow-text bg-gradient-to-r from-ml-accent via-yellow-300 to-ml-accent bg-clip-text text-transparent">
                  MOBILE LEGENDS
                </h1>
                <p className="text-ml-cyan text-sm md:text-base font-semibold tracking-wide uppercase">
                  Draft Pick Assistant with AI-powered hero recommendations
                </p>
              </div>
            </div>
            <div className="hidden md:flex gap-3 items-center">
              <a
                href="/"
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 rounded-xl shadow-lg hover:shadow-blue-500/50 transition-all hover:scale-105 flex items-center gap-2 border-2 border-blue-400/50"
              >
                <span className="text-xl">←</span>
                <div>
                  <div className="text-white font-bold text-sm uppercase tracking-wider">Back to Chat</div>
                  <div className="text-blue-200 text-xs">AI Assistant</div>
                </div>
              </a>
            </div>
          </div>
        </div>
        {/* Shine effect */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-ml-accent to-transparent"></div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 max-w-7xl relative">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Draft State */}
          <div className="lg:col-span-1 space-y-4">
            {/* Lane Selection */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-purple-500/30">
              <h2 className="text-xl font-bold text-white mb-4">📍 Your Lane</h2>
              <div className="grid grid-cols-2 gap-2">
                {LANES.map(lane => (
                  <button
                    key={lane}
                    onClick={() => setUserLane(lane)}
                    className={`px-4 py-3 rounded-lg font-medium transition-all ${
                      userLane === lane
                        ? `${LANE_COLORS[lane as keyof typeof LANE_COLORS]} text-white shadow-lg scale-105`
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    {LANE_LABELS[lane as keyof typeof LANE_LABELS]}
                  </button>
                ))}
              </div>
            </div>

            {/* Draft Lists */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-purple-500/30">
              <div className="flex space-x-2 mb-4">
                <button
                  onClick={() => setActiveTab('banned')}
                  className={`flex-1 py-2 px-3 rounded-lg font-medium transition-colors ${
                    activeTab === 'banned' ? 'bg-red-500 text-white' : 'bg-slate-700 text-slate-300'
                  }`}
                >
                  🚫 Banned ({banned.length})
                </button>
                <button
                  onClick={() => setActiveTab('enemy')}
                  className={`flex-1 py-2 px-3 rounded-lg font-medium transition-colors ${
                    activeTab === 'enemy' ? 'bg-orange-500 text-white' : 'bg-slate-700 text-slate-300'
                  }`}
                >
                  ⚔️ Enemy ({enemy.length})
                </button>
                <button
                  onClick={() => setActiveTab('team')}
                  className={`flex-1 py-2 px-3 rounded-lg font-medium transition-colors ${
                    activeTab === 'team' ? 'bg-blue-500 text-white' : 'bg-slate-700 text-slate-300'
                  }`}
                >
                  👥 Team ({team.length})
                </button>
              </div>

              {/* Lane Selector for Team */}
              {activeTab === 'team' && (
                <div className="mb-3">
                  <label className="text-xs text-slate-400 mb-2 block">Select Lane:</label>
                  <div className="grid grid-cols-5 gap-2">
                    {LANES.map(lane => (
                      <button
                        key={lane}
                        onClick={() => setTeamLaneInput(lane)}
                        className={`px-2 py-2 rounded text-xs font-medium transition-all ${
                          teamLaneInput === lane
                            ? `${LANE_COLORS[lane as keyof typeof LANE_COLORS]} text-white shadow-lg`
                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                        }`}
                        disabled={team.some(h => h.endsWith(`-${lane}`))}
                      >
                        {LANE_LABELS[lane as keyof typeof LANE_LABELS]}
                        {team.some(h => h.endsWith(`-${lane}`)) && ' ✓'}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Hero Search */}
              <input
                type="text"
                placeholder={activeTab === 'team' ? "Search hero..." : "Search hero to add..."}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 bg-slate-700 rounded-lg text-white placeholder-slate-400 mb-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />

              {/* Search Results */}
              {searchQuery && (
                <div className="max-h-48 overflow-y-auto mb-4 bg-slate-900/50 rounded-lg">
                  {filteredHeroes.slice(0, 10).map(hero => (
                    <button
                      key={hero.name}
                      onClick={() => activeTab === 'team' ? addHeroWithLane(hero.name, teamLaneInput) : addHeroToList(hero.name, activeTab)}
                      className="w-full text-left px-3 py-2 hover:bg-slate-700 transition-colors text-white"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium capitalize">{hero.name}</div>
                          <div className="text-xs text-slate-400">
                            {hero.roles.join(', ')} • {hero.lanes.join(', ')}
                          </div>
                        </div>
                        {activeTab === 'team' && (
                          <span className={`text-xs px-2 py-1 rounded ${LANE_COLORS[teamLaneInput as keyof typeof LANE_COLORS]}`}>
                            {teamLaneInput}
                          </span>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Selected Heroes List */}
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {activeTab === 'banned' && banned.map(hero => (
                  <div key={hero} className="flex items-center justify-between bg-red-500/20 px-3 py-2 rounded-lg">
                    <span className="text-white capitalize font-medium">{hero}</span>
                    <button
                      onClick={() => removeHeroFromList(hero, 'banned')}
                      className="text-red-400 hover:text-red-300"
                    >
                      ✕
                    </button>
                  </div>
                ))}
                {activeTab === 'enemy' && enemy.map(hero => (
                  <div key={hero} className="flex items-center justify-between bg-orange-500/20 px-3 py-2 rounded-lg">
                    <span className="text-white capitalize font-medium">{hero}</span>
                    <button
                      onClick={() => removeHeroFromList(hero, 'enemy')}
                      className="text-orange-400 hover:text-orange-300"
                    >
                      ✕
                    </button>
                  </div>
                ))}
                {activeTab === 'team' && team.map(heroWithLane => {
                  const heroName = heroWithLane.split('-')[0];
                  const lane = getHeroLane(heroWithLane);
                  return (
                    <div key={heroWithLane} className="flex items-center justify-between bg-blue-500/20 px-3 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <span className="text-white capitalize font-medium">{heroName}</span>
                        {lane && (
                          <span className={`text-xs px-2 py-1 rounded ${LANE_COLORS[lane as keyof typeof LANE_COLORS]}`}>
                            {lane}
                          </span>
                        )}
                      </div>
                      <button
                        onClick={() => removeHeroFromList(heroName, 'team')}
                        className="text-blue-400 hover:text-blue-300"
                      >
                        ✕
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-2">
              <button
                onClick={getDraftRecommendations}
                disabled={loading}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '🔄 Loading...' : '🎯 Get Recommendations'}
              </button>
              <button
                onClick={resetDraft}
                className="w-full bg-slate-700 hover:bg-slate-600 text-white font-medium py-2 px-6 rounded-xl transition-colors"
              >
                🔄 Reset Draft
              </button>
            </div>
          </div>

          {/* Right Panel - Recommendations */}
          <div className="lg:col-span-2 space-y-4">
            {/* Team Analysis */}
            {teamAnalysis && (
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-purple-500/30">
                <h2 className="text-xl font-bold text-white mb-4">📊 Team Analysis</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-slate-400 mb-2">Lane Coverage</h3>
                    <div className="space-y-1">
                      {Object.entries(teamAnalysis.lane_counts).map(([lane, count]) => (
                        <div key={lane} className="flex items-center justify-between text-sm">
                          <span className="text-white capitalize">{lane}</span>
                          <span className={`px-2 py-0.5 rounded ${count > 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                            {count > 0 ? '✓' : '✗'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-slate-400 mb-2">Role Distribution</h3>
                    <div className="space-y-1">
                      {Object.entries(teamAnalysis.role_counts).map(([role, count]) => (
                        count > 0 && (
                          <div key={role} className="flex items-center justify-between text-sm">
                            <span className="text-white capitalize">{role}</span>
                            <span className="text-purple-400">{count}</span>
                          </div>
                        )
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-slate-400 mb-2">Balance</h3>
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-white">Damage Balance</span>
                        <span className={`px-2 py-0.5 rounded ${
                          teamAnalysis.damage_balance === 'balanced' 
                            ? 'bg-green-500/20 text-green-400' 
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {teamAnalysis.damage_balance}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-white">Jungle-Roam</span>
                        <span className={`px-2 py-0.5 rounded ${
                          teamAnalysis.jungle_roam_valid === 'valid' 
                            ? 'bg-green-500/20 text-green-400' 
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {teamAnalysis.jungle_roam_valid}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-slate-400 mb-2">Diversity</h3>
                    <div className="text-2xl font-bold text-purple-400">
                      {teamAnalysis.role_diversity} roles
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Recommendations List */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-purple-500/30">
              <h2 className="text-xl font-bold text-white mb-4">
                ⭐ Recommended Heroes
                {recommendations.length > 0 && ` (${recommendations.length})`}
              </h2>

              {recommendations.length === 0 ? (
                <div className="text-center py-12 text-slate-400">
                  <div className="text-4xl mb-2">🎮</div>
                  <p>Click "Get Recommendations" to see hero suggestions</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {recommendations.map((rec, index) => (
                    <div
                      key={rec.hero}
                      className="bg-gradient-to-r from-slate-700/50 to-slate-800/50 p-4 rounded-lg border border-purple-500/20 hover:border-purple-500/50 transition-all"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <div className="text-2xl font-bold text-purple-400">#{index + 1}</div>
                          <div>
                            <h3 className="text-lg font-bold text-white capitalize">{rec.hero}</h3>
                            <div className="text-sm text-purple-300">
                              Priority Score: {rec.priority.toFixed(1)}
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => addHeroToList(rec.hero, 'team')}
                          className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded-lg text-sm transition-colors"
                        >
                          + Add to Team
                        </button>
                      </div>
                      <div className="space-y-1">
                        {rec.reasons.map((reason, i) => (
                          <div key={i} className="text-sm text-slate-300 flex items-start">
                            <span className="text-green-400 mr-2">✓</span>
                            <span>{reason}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map(toast => (
          <div
            key={toast.id}
            className={`min-w-[300px] px-6 py-4 rounded-lg shadow-2xl backdrop-blur-md border-2 animate-slide-in-right flex items-start gap-3 ${
              toast.type === 'success'
                ? 'bg-green-500/90 border-green-400 text-white'
                : toast.type === 'error'
                ? 'bg-red-500/90 border-red-400 text-white'
                : toast.type === 'warning'
                ? 'bg-yellow-500/90 border-yellow-400 text-white'
                : 'bg-blue-500/90 border-blue-400 text-white'
            }`}
          >
            <div className="text-2xl">
              {toast.type === 'success' ? '✓' : toast.type === 'error' ? '✕' : toast.type === 'warning' ? '⚠' : 'ℹ'}
            </div>
            <div className="flex-1">
              <p className="font-medium">{toast.message}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <footer className="py-3 border-t border-ml-accent/20 backdrop-blur-sm bg-ml-primary/30 relative">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-ml-light/70">
            IF4070 Representasi Pengetahuan dan Penalaran
          </p>
        </div>
      </footer>
    </div>
  );
}
