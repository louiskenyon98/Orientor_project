import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  MapPin, 
  Clock, 
  DollarSign, 
  Building2, 
  Users, 
  Star, 
  TrendingUp,
  Bookmark,
  ExternalLink,
  Heart
} from 'lucide-react';

export interface JobCardProps {
  job: {
    id: string;
    title: string;
    company: string;
    location: string;
    type: 'Full-time' | 'Part-time' | 'Contract' | 'Internship';
    salary?: {
      min: number;
      max: number;
      currency: string;
    };
    matchPercentage: number;
    description: string;
    requirements: string[];
    skills: string[];
    postedDate: string;
    applicants?: number;
    companyLogo?: string;
    isRemote?: boolean;
    experienceLevel: 'Entry' | 'Mid' | 'Senior' | 'Lead';
    industry: string;
    benefits?: string[];
    isSaved?: boolean;
    isLiked?: boolean;
  };
  onSave?: (jobId: string) => void;
  onLike?: (jobId: string) => void;
  onApply?: (jobId: string) => void;
  variant?: 'default' | 'compact' | 'detailed';
}

const JobCard: React.FC<JobCardProps> = ({ 
  job, 
  onSave, 
  onLike, 
  onApply, 
  variant = 'default' 
}) => {
  const formatSalary = (salary: typeof job.salary) => {
    if (!salary) return 'Salary not disclosed';
    return `${salary.currency}${salary.min.toLocaleString()} - ${salary.currency}${salary.max.toLocaleString()}`;
  };

  const getMatchColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-green-500 text-white';
    if (percentage >= 75) return 'bg-blue-500 text-white';
    if (percentage >= 60) return 'bg-yellow-500 text-white';
    return 'bg-gray-500 text-white';
  };

  const getExperienceColor = (level: string) => {
    switch (level) {
      case 'Entry': return 'bg-green-100 text-green-800';
      case 'Mid': return 'bg-blue-100 text-blue-800';
      case 'Senior': return 'bg-purple-100 text-purple-800';
      case 'Lead': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (variant === 'compact') {
    return (
      <Card className="hover:shadow-lg transition-all duration-300 border-l-4 border-l-blue-500 cursor-pointer">
        <CardContent className="p-4">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <h3 className="font-semibold text-lg mb-1">{job.title}</h3>
              <p className="text-gray-600 text-sm flex items-center">
                <Building2 className="w-3 h-3 mr-1" />
                {job.company}
              </p>
            </div>
            <Badge className={`ml-2 ${getMatchColor(job.matchPercentage)}`}>
              {job.matchPercentage}% Match
            </Badge>
          </div>
          
          <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
            <span className="flex items-center">
              <MapPin className="w-3 h-3 mr-1" />
              {job.location} {job.isRemote && '(Remote)'}
            </span>
            <span className="flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {job.postedDate}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <Badge variant="outline" className={getExperienceColor(job.experienceLevel)}>
              {job.experienceLevel}
            </Badge>
            <Button size="sm" onClick={() => onApply?.(job.id)}>
              Apply
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (variant === 'detailed') {
    return (
      <Card className="hover:shadow-xl transition-all duration-300 border-t-4 border-t-blue-500">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4">
              {job.companyLogo && (
                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-gray-600" />
                </div>
              )}
              <div>
                <CardTitle className="text-xl mb-2">{job.title}</CardTitle>
                <p className="text-gray-600 flex items-center mb-1">
                  <Building2 className="w-4 h-4 mr-2" />
                  {job.company}
                </p>
                <p className="text-gray-500 text-sm flex items-center">
                  <MapPin className="w-3 h-3 mr-1" />
                  {job.location} {job.isRemote && '• Remote'}
                </p>
              </div>
            </div>
            <div className="flex flex-col items-end space-y-2">
              <Badge className={getMatchColor(job.matchPercentage)}>
                <Star className="w-3 h-3 mr-1" />
                {job.matchPercentage}% Match
              </Badge>
              <div className="flex space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onSave?.(job.id)}
                  className={job.isSaved ? 'text-blue-600' : 'text-gray-400'}
                >
                  <Bookmark className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onLike?.(job.id)}
                  className={job.isLiked ? 'text-red-600' : 'text-gray-400'}
                >
                  <Heart className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Job Details */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-t border-b border-gray-100">
            <div className="text-center">
              <DollarSign className="w-5 h-5 mx-auto text-green-600 mb-1" />
              <p className="text-xs text-gray-500">Salary</p>
              <p className="text-sm font-medium">{formatSalary(job.salary)}</p>
            </div>
            <div className="text-center">
              <Clock className="w-5 h-5 mx-auto text-blue-600 mb-1" />
              <p className="text-xs text-gray-500">Type</p>
              <p className="text-sm font-medium">{job.type}</p>
            </div>
            <div className="text-center">
              <TrendingUp className="w-5 h-5 mx-auto text-purple-600 mb-1" />
              <p className="text-xs text-gray-500">Level</p>
              <p className="text-sm font-medium">{job.experienceLevel}</p>
            </div>
            <div className="text-center">
              <Users className="w-5 h-5 mx-auto text-orange-600 mb-1" />
              <p className="text-xs text-gray-500">Applicants</p>
              <p className="text-sm font-medium">{job.applicants || 'N/A'}</p>
            </div>
          </div>
          
          {/* Description */}
          <div>
            <h4 className="font-medium mb-2">Job Description</h4>
            <p className="text-gray-600 text-sm leading-relaxed">{job.description}</p>
          </div>
          
          {/* Skills */}
          <div>
            <h4 className="font-medium mb-3">Required Skills</h4>
            <div className="flex flex-wrap gap-2">
              {job.skills.map((skill) => (
                <Badge key={skill} variant="secondary" className="text-xs">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
          
          {/* Benefits */}
          {job.benefits && job.benefits.length > 0 && (
            <div>
              <h4 className="font-medium mb-3">Benefits</h4>
              <div className="grid grid-cols-2 gap-2">
                {job.benefits.map((benefit) => (
                  <div key={benefit} className="flex items-center text-sm text-gray-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    {benefit}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Actions */}
          <div className="flex space-x-3 pt-4">
            <Button 
              className="flex-1 bg-blue-600 hover:bg-blue-700"
              onClick={() => onApply?.(job.id)}
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              Apply Now
            </Button>
            <Button variant="outline" onClick={() => onSave?.(job.id)}>
              Save for Later
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Default variant
  return (
    <Card className="hover:shadow-lg transition-all duration-300 cursor-pointer group">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <CardTitle className="text-lg group-hover:text-blue-600 transition-colors">
                {job.title}
              </CardTitle>
              <Badge className={getMatchColor(job.matchPercentage)}>
                {job.matchPercentage}%
              </Badge>
            </div>
            <p className="text-gray-600 flex items-center mb-1">
              <Building2 className="w-4 h-4 mr-2" />
              {job.company}
            </p>
            <p className="text-gray-500 text-sm flex items-center">
              <MapPin className="w-3 h-3 mr-1" />
              {job.location} {job.isRemote && '• Remote'}
            </p>
          </div>
          <div className="flex space-x-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onSave?.(job.id);
              }}
              className={job.isSaved ? 'text-blue-600' : 'text-gray-400'}
            >
              <Bookmark className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onLike?.(job.id);
              }}
              className={job.isLiked ? 'text-red-600' : 'text-gray-400'}
            >
              <Heart className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <p className="text-gray-600 text-sm line-clamp-2">{job.description}</p>
        
        <div className="flex flex-wrap gap-2">
          {job.skills.slice(0, 3).map((skill) => (
            <Badge key={skill} variant="outline" className="text-xs">
              {skill}
            </Badge>
          ))}
          {job.skills.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{job.skills.length - 3} more
            </Badge>
          )}
        </div>
        
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-4">
            <span className="flex items-center">
              <DollarSign className="w-3 h-3 mr-1" />
              {formatSalary(job.salary)}
            </span>
            <Badge variant="outline" className={getExperienceColor(job.experienceLevel)}>
              {job.experienceLevel}
            </Badge>
          </div>
          <span className="flex items-center">
            <Clock className="w-3 h-3 mr-1" />
            {job.postedDate}
          </span>
        </div>
        
        <div className="flex space-x-2 pt-2">
          <Button 
            size="sm" 
            className="flex-1"
            onClick={(e) => {
              e.stopPropagation();
              onApply?.(job.id);
            }}
          >
            Apply
          </Button>
          <Button 
            size="sm" 
            variant="outline"
            onClick={(e) => {
              e.stopPropagation();
              // View details action
            }}
          >
            Details
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default JobCard;