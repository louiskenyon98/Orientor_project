'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import MainLayout from '@/components/layout/MainLayout';
import educationService, { 
  Program, 
  ProgramSearchRequest, 
  SearchMetadata,
  Institution 
} from '@/services/educationService';

// Search and Filter Components
interface SearchFiltersProps {
  metadata: SearchMetadata | null;
  onSearch: (request: ProgramSearchRequest) => void;
  isLoading: boolean;
}

const SearchFilters: React.FC<SearchFiltersProps> = ({ metadata, onSearch, isLoading }) => {
  const [query, setQuery] = useState('');
  const [selectedInstitutionTypes, setSelectedInstitutionTypes] = useState<string[]>([]);
  const [selectedLevels, setSelectedLevels] = useState<string[]>([]);
  const [selectedCities, setSelectedCities] = useState<string[]>([]);
  const [selectedFields, setSelectedFields] = useState<string[]>([]);
  const [maxTuition, setMaxTuition] = useState<number | undefined>();
  const [minEmploymentRate, setMinEmploymentRate] = useState<number | undefined>();
  const [hollandMatching, setHollandMatching] = useState(true);

  const handleSearch = () => {
    const searchRequest: ProgramSearchRequest = {
      query: query.trim() || undefined,
      institution_types: selectedInstitutionTypes.length > 0 ? selectedInstitutionTypes as any : undefined,
      program_levels: selectedLevels.length > 0 ? selectedLevels as any : undefined,
      cities: selectedCities.length > 0 ? selectedCities : undefined,
      fields_of_study: selectedFields.length > 0 ? selectedFields : undefined,
      max_tuition: maxTuition,
      min_employment_rate: minEmploymentRate,
      holland_matching: hollandMatching,
      user_id: 1, // In production, get from auth context
      limit: 20,
      offset: 0,
    };

    onSearch(searchRequest);
  };

  const clearFilters = () => {
    setQuery('');
    setSelectedInstitutionTypes([]);
    setSelectedLevels([]);
    setSelectedCities([]);
    setSelectedFields([]);
    setMaxTuition(undefined);
    setMinEmploymentRate(undefined);
    setHollandMatching(true);
    
    // Trigger search with cleared filters
    onSearch({
      holland_matching: true,
      user_id: 1,
      limit: 20,
      offset: 0,
    });
  };

  return (
    <div className="bg-stitch-primary border border-stitch-border rounded-lg p-6 mb-8">
      <h2 className="text-2xl font-bold text-stitch-accent mb-6">Search & Filter Programs</h2>
      
      {/* Search Bar */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-stitch-sage mb-2">
          Search Programs
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by program name, field, or institution..."
            className="flex-1 px-4 py-2 bg-stitch-primary border border-stitch-border rounded-md text-stitch-sage placeholder-stitch-sage/70 focus:ring-2 focus:ring-stitch-accent focus:border-transparent"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="px-6 py-2 bg-stitch-accent text-white rounded-md hover:bg-stitch-accent/90 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {/* Filters Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        {/* Institution Type */}
        <div>
          <label className="block text-sm font-medium text-stitch-sage mb-2">
            Institution Type
          </label>
          <div className="space-y-2">
            {metadata?.institution_types.map((type) => (
              <label key={type} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedInstitutionTypes.includes(type)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedInstitutionTypes([...selectedInstitutionTypes, type]);
                    } else {
                      setSelectedInstitutionTypes(selectedInstitutionTypes.filter(t => t !== type));
                    }
                  }}
                  className="mr-2 text-stitch-accent focus:ring-stitch-accent"
                />
                <span className="text-stitch-sage capitalize">{type}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Program Level */}
        <div>
          <label className="block text-sm font-medium text-stitch-sage mb-2">
            Program Level
          </label>
          <div className="space-y-2">
            {metadata?.program_levels.map((level) => (
              <label key={level} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedLevels.includes(level)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedLevels([...selectedLevels, level]);
                    } else {
                      setSelectedLevels(selectedLevels.filter(l => l !== level));
                    }
                  }}
                  className="mr-2 text-stitch-accent focus:ring-stitch-accent"
                />
                <span className="text-stitch-sage capitalize">{level}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Cities */}
        <div>
          <label className="block text-sm font-medium text-stitch-sage mb-2">
            Cities
          </label>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {metadata?.cities.slice(0, 5).map((city) => (
              <label key={city} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedCities.includes(city)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedCities([...selectedCities, city]);
                    } else {
                      setSelectedCities(selectedCities.filter(c => c !== city));
                    }
                  }}
                  className="mr-2 text-stitch-accent focus:ring-stitch-accent"
                />
                <span className="text-stitch-sage">{city}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Field of Study */}
        <div>
          <label className="block text-sm font-medium text-stitch-sage mb-2">
            Field of Study
          </label>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {metadata?.fields_of_study.map((field) => (
              <label key={field} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedFields.includes(field)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedFields([...selectedFields, field]);
                    } else {
                      setSelectedFields(selectedFields.filter(f => f !== field));
                    }
                  }}
                  className="mr-2 text-stitch-accent focus:ring-stitch-accent"
                />
                <span className="text-stitch-sage">{field}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Max Tuition */}
        <div>
          <label className="block text-sm font-medium text-stitch-sage mb-2">
            Max Tuition (CAD)
          </label>
          <input
            type="number"
            value={maxTuition || ''}
            onChange={(e) => setMaxTuition(e.target.value ? Number(e.target.value) : undefined)}
            placeholder="e.g. 5000"
            className="w-full px-3 py-2 bg-stitch-primary border border-stitch-border rounded-md text-stitch-sage focus:ring-2 focus:ring-stitch-accent"
          />
        </div>

        {/* Min Employment Rate */}
        <div>
          <label className="block text-sm font-medium text-stitch-sage mb-2">
            Min Employment Rate (%)
          </label>
          <input
            type="number"
            value={minEmploymentRate || ''}
            onChange={(e) => setMinEmploymentRate(e.target.value ? Number(e.target.value) : undefined)}
            placeholder="e.g. 85"
            min="0"
            max="100"
            className="w-full px-3 py-2 bg-stitch-primary border border-stitch-border rounded-md text-stitch-sage focus:ring-2 focus:ring-stitch-accent"
          />
        </div>
      </div>

      {/* Holland Matching Toggle */}
      <div className="mb-6">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={hollandMatching}
            onChange={(e) => setHollandMatching(e.target.checked)}
            className="mr-2 text-stitch-accent focus:ring-stitch-accent"
          />
          <span className="text-stitch-sage font-medium">
            Enable personality-based matching (Holland RIASEC)
          </span>
        </label>
        <p className="text-sm text-stitch-sage/70 mt-1">
          When enabled, programs are sorted by compatibility with your personality profile
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleSearch}
          disabled={isLoading}
          className="px-6 py-2 bg-stitch-accent text-white rounded-md hover:bg-stitch-accent/90 disabled:opacity-50 font-medium"
        >
          Apply Filters
        </button>
        <button
          onClick={clearFilters}
          className="px-6 py-2 border border-stitch-border text-stitch-sage rounded-md hover:bg-stitch-primary/50 font-medium"
        >
          Clear All
        </button>
      </div>
    </div>
  );
};

// Enhanced Program Card Component
interface ProgramCardProps {
  program: Program;
  onSave: (programId: string) => void;
  onUnsave: (programId: string) => void;
  isSaved: boolean;
}

const ProgramCard: React.FC<ProgramCardProps> = ({ program, onSave, onUnsave, isSaved }) => {
  const compatibilityPercentage = educationService.calculateCompatibilityPercentage(program.holland_compatibility);
  const topTraits = educationService.getTopHollandTraits(program.holland_compatibility);
  const tuitionFormatted = educationService.formatTuition(program.tuition_domestic, true);

  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="bg-stitch-primary border border-stitch-border rounded-lg p-6 shadow-lg hover:shadow-xl transition-all duration-300"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-stitch-accent mb-1">{program.title}</h3>
          <p className="text-stitch-sage">{program.institution.name}</p>
          <p className="text-sm text-stitch-sage/70">{program.institution.city}, {program.institution.province_state}</p>
        </div>
        <div className="text-right">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            program.institution.institution_type === 'cegep' 
              ? 'bg-blue-100 text-blue-800' 
              : program.institution.institution_type === 'university'
              ? 'bg-purple-100 text-purple-800'
              : 'bg-green-100 text-green-800'
          }`}>
            {program.institution.institution_type.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Program Details Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-stitch-sage/70">Level</p>
          <p className="font-semibold text-stitch-accent capitalize">{program.level}</p>
        </div>
        <div>
          <p className="text-sm text-stitch-sage/70">Duration</p>
          <p className="font-semibold text-stitch-accent">
            {program.duration_months ? `${program.duration_months} months` : 'Not specified'}
          </p>
        </div>
        <div>
          <p className="text-sm text-stitch-sage/70">Tuition</p>
          <p className="font-semibold text-stitch-accent">{tuitionFormatted}</p>
        </div>
        <div>
          <p className="text-sm text-stitch-sage/70">Employment Rate</p>
          <p className="font-semibold text-green-600">
            {program.employment_rate ? `${program.employment_rate}%` : 'N/A'}
          </p>
        </div>
      </div>

      {/* Field of Study */}
      <div className="mb-4">
        <p className="text-sm text-stitch-sage/70 mb-1">Field of Study</p>
        <span className="inline-block bg-stitch-accent/10 text-stitch-accent px-3 py-1 rounded-full text-sm font-medium">
          {program.field_of_study}
        </span>
      </div>

      {/* Holland Compatibility */}
      {program.holland_compatibility && (
        <div className="mb-4 bg-stitch-accent/5 rounded-lg p-3">
          <div className="flex justify-between items-center mb-2">
            <p className="text-sm font-medium text-stitch-accent">Personality Match</p>
            <p className="text-lg font-bold text-stitch-accent">{compatibilityPercentage}%</p>
          </div>
          <p className="text-sm text-stitch-sage">
            Best fit for: {topTraits.join(', ')} personalities
          </p>
        </div>
      )}

      {/* Description */}
      <p className="text-stitch-sage mb-4 line-clamp-3">{program.description}</p>

      {/* Career Outcomes */}
      {program.career_outcomes.length > 0 && (
        <div className="mb-4">
          <p className="text-sm text-stitch-sage/70 mb-2">Career Paths</p>
          <div className="flex flex-wrap gap-1">
            {program.career_outcomes.slice(0, 3).map((outcome, index) => (
              <span 
                key={index}
                className="inline-block bg-stitch-accent/10 text-stitch-accent px-2 py-1 rounded text-xs"
              >
                {outcome}
              </span>
            ))}
            {program.career_outcomes.length > 3 && (
              <span className="inline-block text-stitch-sage/70 px-2 py-1 text-xs">
                +{program.career_outcomes.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={() => isSaved ? onUnsave(program.id) : onSave(program.id)}
          className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            isSaved
              ? 'bg-green-100 text-green-800 border border-green-300'
              : 'bg-stitch-accent text-white hover:bg-stitch-accent/90'
          }`}
        >
          {isSaved ? '✓ Saved' : 'Save Program'}
        </button>
        <button 
          onClick={() => window.open(program.institution.website_url, '_blank')}
          className="px-4 py-2 border border-stitch-border text-stitch-accent rounded-md hover:bg-stitch-accent/5 transition-colors text-sm font-medium"
        >
          Learn More
        </button>
      </div>
    </motion.div>
  );
};

// Main Education Page Component
export default function EducationPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [metadata, setMetadata] = useState<SearchMetadata | null>(null);
  const [savedPrograms, setSavedPrograms] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchMetadata, setSearchMetadata] = useState<any>(null);
  const [hasSearched, setHasSearched] = useState(false);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Load search metadata
        const metadataResponse = await educationService.getSearchMetadata();
        setMetadata(metadataResponse);

        // Load personalized recommendations
        const recommendationsResponse = await educationService.getPersonalizedRecommendations(1, 20);
        setPrograms(recommendationsResponse.programs);
        setSearchMetadata(recommendationsResponse.search_metadata);

        // Load saved programs (mock for now)
        setSavedPrograms(['dawson-computer-science']);

      } catch (err) {
        console.error('Error loading initial data:', err);
        setError('Failed to load education programs. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, []);

  const handleSearch = async (searchRequest: ProgramSearchRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      setHasSearched(true);

      const response = await educationService.searchPrograms(searchRequest);
      setPrograms(response.programs);
      setSearchMetadata(response.search_metadata);

    } catch (err) {
      console.error('Error searching programs:', err);
      setError('Failed to search programs. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveProgram = async (programId: string) => {
    try {
      await educationService.saveProgram(programId, 1);
      setSavedPrograms(prev => [...prev, programId]);
    } catch (err) {
      console.error('Error saving program:', err);
    }
  };

  const handleUnsaveProgram = async (programId: string) => {
    try {
      await educationService.unsaveProgram(programId, 1);
      setSavedPrograms(prev => prev.filter(id => id !== programId));
    } catch (err) {
      console.error('Error unsaving program:', err);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-stitch-accent mb-4">Education Programs</h1>
          <p className="text-xl text-stitch-sage max-w-3xl mx-auto">
            Search and discover educational programs in Quebec tailored to your interests and career goals
          </p>
        </motion.div>

        {/* Search and Filters */}
        <SearchFilters 
          metadata={metadata}
          onSearch={handleSearch}
          isLoading={isLoading}
        />

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Results Header */}
        {searchMetadata && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6"
          >
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-stitch-accent">
                  {hasSearched ? 'Search Results' : 'Recommended for You'}
                </h2>
                <p className="text-stitch-sage">
                  {searchMetadata.holland_matching_enabled ? 
                    `Found ${programs.length} programs sorted by personality match` :
                    `Found ${programs.length} programs`
                  }
                </p>
              </div>
              <div className="text-right text-sm text-stitch-sage/70">
                {searchMetadata.total_available_programs} total programs available
              </div>
            </div>
          </motion.div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-stitch-accent"></div>
            <span className="ml-3 text-stitch-sage">Loading programs...</span>
          </div>
        )}

        {/* Programs Grid */}
        {!isLoading && programs.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-12"
          >
            {programs.map((program) => (
              <ProgramCard
                key={program.id}
                program={program}
                onSave={handleSaveProgram}
                onUnsave={handleUnsaveProgram}
                isSaved={savedPrograms.includes(program.id)}
              />
            ))}
          </motion.div>
        )}

        {/* No Results */}
        {!isLoading && programs.length === 0 && hasSearched && (
          <div className="text-center py-12">
            <h3 className="text-xl font-semibold text-stitch-accent mb-2">No programs found</h3>
            <p className="text-stitch-sage mb-4">
              Try adjusting your search criteria or removing some filters.
            </p>
          </div>
        )}

        {/* Quick Stats */}
        {searchMetadata && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-stitch-accent/5 rounded-lg p-6"
          >
            <h2 className="text-2xl font-bold text-stitch-accent mb-4">Search Summary</h2>
            <div className="grid md:grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-3xl font-bold text-stitch-accent">{programs.length}</p>
                <p className="text-stitch-sage">Programs Found</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-stitch-accent">{savedPrograms.length}</p>
                <p className="text-stitch-sage">Programs Saved</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-stitch-accent">
                  {searchMetadata.holland_matching_enabled ? 'ON' : 'OFF'}
                </p>
                <p className="text-stitch-sage">Personality Matching</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </MainLayout>
  );
}