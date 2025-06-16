/**
 * Search Filters Component for School Programs
 */

import React from 'react';
import { Filter } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { SearchFilters as ISearchFilters, SearchResults } from './types';

interface SearchFiltersProps {
  filters: ISearchFilters;
  onFiltersChange: (filters: ISearchFilters) => void;
  facets: SearchResults['facets'];
}

const SearchFilters: React.FC<SearchFiltersProps> = ({ filters, onFiltersChange, facets }) => {
  const updateFilter = (key: string, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    });
  };

  const updateLocationFilter = (key: string, value: string) => {
    onFiltersChange({
      ...filters,
      location: {
        ...filters.location,
        [key]: value,
      },
    });
  };

  const toggleArrayFilter = (key: string, value: string) => {
    const currentArray = filters[key as keyof ISearchFilters] as string[];
    const newArray = currentArray.includes(value)
      ? currentArray.filter(item => item !== value)
      : [...currentArray, value];
    
    updateFilter(key, newArray);
  };

  const clearAllFilters = () => {
    onFiltersChange({
      text: '',
      program_types: [],
      levels: [],
      location: {},
      languages: [],
      duration: {},
      budget: { currency: 'CAD' },
    });
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Filter className="h-5 w-5" />
          Search Filters
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Clear Filters Button */}
        <Button variant="outline" onClick={clearAllFilters} className="w-full">
          Clear All Filters
        </Button>

        {/* Program Types */}
        <div>
          <label className="text-sm font-medium mb-2 block">Program Type</label>
          <div className="space-y-2">
            {Object.entries(facets.program_types).map(([type, count]) => (
              <div key={type} className="flex items-center space-x-2">
                <Checkbox
                  id={`type-${type}`}
                  checked={filters.program_types.includes(type)}
                  onCheckedChange={() => toggleArrayFilter('program_types', type)}
                />
                <label htmlFor={`type-${type}`} className="text-sm cursor-pointer">
                  {type.charAt(0).toUpperCase() + type.slice(1)} ({count})
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Education Levels */}
        <div>
          <label className="text-sm font-medium mb-2 block">Education Level</label>
          <div className="space-y-2">
            {Object.entries(facets.levels).map(([level, count]) => (
              <div key={level} className="flex items-center space-x-2">
                <Checkbox
                  id={`level-${level}`}
                  checked={filters.levels.includes(level)}
                  onCheckedChange={() => toggleArrayFilter('levels', level)}
                />
                <label htmlFor={`level-${level}`} className="text-sm cursor-pointer">
                  {level.charAt(0).toUpperCase() + level.slice(1)} ({count})
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Location */}
        <div>
          <label className="text-sm font-medium mb-2 block">Location</label>
          <div className="space-y-3">
            <Select 
              value={filters.location.province || ''} 
              onValueChange={(value) => updateLocationFilter('province', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select Province" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Provinces</SelectItem>
                {Object.entries(facets.provinces).map(([province, count]) => (
                  <SelectItem key={province} value={province}>
                    {province} ({count})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Languages */}
        <div>
          <label className="text-sm font-medium mb-2 block">Language</label>
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="lang-en"
                checked={filters.languages.includes('en')}
                onCheckedChange={() => toggleArrayFilter('languages', 'en')}
              />
              <label htmlFor="lang-en" className="text-sm cursor-pointer">English</label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="lang-fr"
                checked={filters.languages.includes('fr')}
                onCheckedChange={() => toggleArrayFilter('languages', 'fr')}
              />
              <label htmlFor="lang-fr" className="text-sm cursor-pointer">French</label>
            </div>
          </div>
        </div>

        {/* Duration */}
        <div>
          <label className="text-sm font-medium mb-2 block">Maximum Duration (months)</label>
          <Input
            type="number"
            value={filters.duration.max_months || ''}
            onChange={(e) => updateFilter('duration', { max_months: parseInt(e.target.value) || undefined })}
            placeholder="e.g., 36"
            min="1"
            max="120"
          />
        </div>

        {/* Budget */}
        <div>
          <label className="text-sm font-medium mb-2 block">Maximum Tuition (CAD)</label>
          <Input
            type="number"
            value={filters.budget.max_tuition || ''}
            onChange={(e) => updateFilter('budget', { 
              max_tuition: parseInt(e.target.value) || undefined,
              currency: 'CAD'
            })}
            placeholder="e.g., 10000"
            min="0"
            step="100"
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default SearchFilters;