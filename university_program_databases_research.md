# Comprehensive Research: University Program Banks and APIs Globally

## Executive Summary

This research document provides a comprehensive analysis of university program databases and APIs globally, with a focus on Canadian sources and integration opportunities for career guidance platforms. The findings include actionable data sources with APIs, data feeds, structured access methods, URLs, endpoints, authentication requirements, and data formats.

## 1. Canadian University Program Databases and Government Sources

### 1.1 Statistics Canada - Classification of Instructional Programs (CIP)

**Official Source**: Statistics Canada maintains the official CIP Canada 2021 classification system.

**Key Details**:
- **URL**: https://www.statcan.gc.ca/en/subjects/standard/cip/2021/index
- **Open Data Portal**: https://open.canada.ca/data/en/dataset/e133360f-ae6c-4a7a-8715-850a7a3d7932
- **Data Structure**: 50 2-digit series, 454 4-digit subseries, 2,119 6-digit instructional program classes
- **Authentication**: No authentication required (Open Government Portal)
- **Data Formats**: HTML, PDF, CSV (English and French)
- **License**: Statistics Canada Open Licence agreement
- **Contact**: infostats@statcan.gc.ca

**API Access**:
- **JSON Metadata**: https://open.canada.ca/data/api/action/package_show?id=e133360f-ae6c-4a7a-8715-850a7a3d7932
- **CSV Downloads**: Available in both English and French
- **Update Cycle**: 10-year revision cycle (latest approved December 14, 2021)

### 1.2 Employment and Social Development Canada (ESDC) - CPIC Database

**Description**: Canadian Post-Secondary Institution Collection database powering EduCanada search tool.

**Key Details**:
- **Search Interface**: https://www.educanada.ca/programs-programmes/template-gabarit/programsearch-rechercheprogramme.aspx?lang=eng
- **Data Source**: ESDC Canadian Post-Secondary Institution Collection (CPIC)
- **Update Frequency**: Yearly updates
- **Coverage**: College and university programs across Canada
- **Authentication**: No API access documented (contact ESDC required)
- **Integration**: Web interface only, no documented API

**Search Parameters**:
- Keyword/field of study
- Language of instruction (English, French, Bilingual)
- Education level
- Province/territory

### 1.3 Canadian University API (Third-Party)

**Description**: Web API for Canadian university program data (eINFO).

**Key Details**:
- **GitHub Repository**: https://github.com/kshvmdn/cdn-university-api
- **Base URL**: localhost:8000 (self-hosted)
- **Endpoint Pattern**: `/api/{program_id}`
- **Authentication**: None required
- **Data Format**: JSON
- **License**: MIT License

**Data Structure**:
```json
{
  "data": {
    "admission": "admission requirements",
    "overview": "program details, degree, enrollment, language",
    "requirements": "program prerequisites"
  }
}
```

## 2. Quebec-Specific University Program Databases and Government APIs

### 2.1 Ministère de l'Éducation du Québec - Open Data

**Official Source**: Quebec Ministry of Education datasets.

**Key Details**:
- **Portal**: https://www.donneesquebec.ca/recherche/organization/mels
- **Authentication**: Open access
- **Data Formats**: CSV, GeoJSON, PDF, XLSX, SHP, KML

**Available Datasets**:
1. Localization of Educational Establishments
2. School Service Center Territories
3. Disadvantage Indices
4. Secondary Professional Training Follow-up Survey

### 2.2 Inforoute FPT (Vocational and Technical Training)

**Description**: Quebec's premier platform for Vocational and Technical Training information.

**Key Details**:
- **URL**: https://www.inforoutefpt.org/
- **English Version**: https://www.inforoutefpt.org/?langue=en
- **Focus**: Vocational and technical training programs
- **Authentication**: No API documented
- **Coverage**: MEES vocational and technical training programs

### 2.3 Bureau de coopération interuniversitaire (BCI)

**Description**: Organization representing 20 Quebec university establishments.

**Key Details**:
- **URL**: https://bci-qc.ca/
- **Services**:
  - Autorisations d'études hors établissement (AEHE): https://aehe.bci-qc.ca/fr/
  - Cote R service for collegiate performance ratings
  - Service de soutien interuniversitaire en RAC (SSIRAC): https://rac.bci-qc.ca/
- **API Access**: No documented public API

**Digital Platforms**:
- Shared Library Services Platform (LSP) - unified catalogue (20+ million documents)
- GéoIndex - geospatial data platform
- Dataverse - research data sharing platform

### 2.4 SRAM (Service Régional d'Admission du Montréal Métropolitain)

**Description**: Processes applications for 32 CEGEPs and public colleges in Quebec.

**Key Details**:
- **URL**: https://www.sram.qc.ca/en
- **Coverage**: 32 CEGEP institutions with 100+ programs
- **API Access**: No documented public API
- **Integration**: Contact SRAM directly for data access

## 3. Major University Program Aggregators and Platforms

### 3.1 College Scorecard API (United States)

**Description**: Comprehensive U.S. higher education institution data API.

**Key Details**:
- **Base URL**: https://api.data.gov/ed/collegescorecard/v1/schools
- **Documentation**: https://collegescorecard.ed.gov/data/api-documentation/
- **Authentication**: API key required (apply at documentation URL)
- **Rate Limit**: 1,000 requests per IP address per hour
- **Data Format**: JSON with XML option
- **Max Page Size**: 100 records

**Key Endpoints**:
- `/v1/schools` - Institution-level data
- Field of study data available as nested arrays
- Search parameters: school.name, school.state, school.city

**Available Data**:
- School information (name, state, city, ownership)
- Student demographics and enrollment
- Academic programs by field of study
- Admission rates, graduation rates, costs
- Financial aid information

### 3.2 Urban Institute Education Data API

**Description**: Comprehensive education database with multiple federal datasets.

**Key Details**:
- **Documentation**: https://educationdata.urban.org/documentation/
- **Data Sources**: 
  - US Department of Education Common Core of Data
  - IPEDS (Integrated Postsecondary Education Data System)
  - College Scorecard
  - Civil Rights Data Collection
- **Access Methods**: Direct URL endpoints, R, Python, Stata, JavaScript
- **Authentication**: Varies by endpoint
- **Data Format**: JSON

### 3.3 EdX Open Data API

**Description**: API for EdX course platform data.

**Key Details**:
- **Documentation**: https://courses.edx.org/api-docs/
- **Authentication**: Basic Authentication with role-based permissions
- **Data Format**: JSON with pagination support

**Key Endpoints**:
1. Course Management - List and retrieve course details
2. Course Home Features - Access course outline, progress, dates
3. Enrollment and Modes - Manage course enrollment
4. Additional APIs - Bookmarks, certificates, cohorts

### 3.4 Coursera Catalog APIs

**Description**: APIs exposing Coursera's course, instructor, and university data.

**Key Details**:
- **Status**: Beta (may change without warning)
- **Authentication**: Public access (no authentication required)
- **Data Format**: JSON
- **Coverage**: Courses, specializations, degrees, instructors, partner universities

**API Behavior**:
- GET to root resource downloads entire collection (with pagination)
- GET with ID path parameter retrieves individual elements
- Can include related data (instructors, partner institutions)

### 3.5 Universities List API

**Description**: Basic university information API.

**Key Details**:
- **Documentation**: https://publicapi.dev/universities-list-api
- **Authentication**: None required
- **Data Format**: JSON
- **Data Fields**: University name, country, domain, website
- **Coverage**: Global university database

**Endpoints**:
- Search universities by name: `GET /universities?name={name}`

## 4. International University Program APIs and Databases

### 4.1 UK - Higher Education Statistics Agency (HESA)

**Description**: Official UK higher education data collection and dissemination agency.

**Key Details**:
- **Organization**: Part of Jisc (merged 2022)
- **Data Portal**: https://www.hesa.ac.uk/data-and-analysis
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Coverage**: 303 HE providers reporting student data (2023/24)

**Data Access Methods**:
1. **Open Data Downloads**: Free under Creative Commons license
2. **Heidi Plus**: Premium visualization tool (institutional access)
3. **HESA Data Platform (HDP)**: For data collection purposes

**Available Data**:
- Student demographics and enrollment
- Graduate outcomes
- Institution finances and estates
- Business and community interaction

### 4.2 Australia - TEQSA National Register

**Description**: Authoritative source for Australian higher education provider status.

**Key Details**:
- **National Register**: https://www.teqsa.gov.au/national-register
- **API Development**: B2G API for real-time data reporting
- **Data Format**: JSON via API, online search interface
- **Coverage**: All registered Australian higher education providers

**Integration Options**:
1. **B2G API**: Direct connection for student management systems
2. **Provider Portal**: Online forms/spreadsheet upload for smaller providers
3. **Search Interface**: Public provider and course search

### 4.3 Europe - European Tertiary Education Register (ETER)

**Description**: Reference dataset on European Higher Education Institutions.

**Key Details**:
- **URL**: https://eter-project.com/
- **Coverage**: ~3,500 HEIs in 40 European countries
- **Data Period**: 2011-2020
- **Standards**: OECD-UNESCO-EUROSTAT compliant

**Data Sources**:
- National Statistical Authorities (NSAs)
- Ministry data from participating countries
- Extensive harmonization and quality checks

**Available Data**:
- Descriptive and geographical information
- Student and graduate statistics (with breakdowns)
- Revenues and expenditures
- Personnel and research activities

### 4.4 European Higher Education Sector Observatory (EHESO)

**Key Features**:
- **Open Access Data Centre**: Microdata access
- **Institutional Benchmarking Tool**: EU and OECD university comparisons
- **Student Observatory**: European study options information

**Integrated Data Sources**:
- ETER (European Tertiary Education Register)
- U-Multirank (institutional benchmarking)
- Erasmus+ database
- DEQAR (Database of External Quality Assurance Results)
- EUROSTUDENT (social dimension data)
- EUROGRADUATE (graduate outcomes)

### 4.5 EUROSTUDENT Database

**Description**: Social dimension of European higher education data.

**Key Details**:
- **URL**: https://database.eurostudent.eu/
- **Focus**: Student social and economic conditions
- **Data Access**: Open database with search functionality
- **Coverage**: European higher education systems

## 5. Academic Program Classification Systems

### 5.1 Classification of Instructional Programs (CIP) - NCES

**Description**: US standard for classifying instructional programs.

**Key Details**:
- **Official Site**: https://nces.ed.gov/ipeds/cipcode/
- **Current Version**: CIP 2020 (Version 6)
- **Next Update**: Expected 2030
- **Structure**: 6-digit codes (xx.xxxx format)

**Data Access**:
- **Browse Tool**: https://nces.ed.gov/ipeds/cipcode/browse.aspx?y=55
- **Search Tool**: https://nces.ed.gov/ipeds/cipcode/search.aspx?y=55
- **API Access**: No direct API (use IPEDS or third-party tools)

**Integration with IPEDS**:
- Required for Title IV institutions
- Available through Urban Institute Education Data API
- CSV downloads available from NCES

### 5.2 International Standard Classification of Education (ISCED) - UNESCO

**Description**: Global framework for organizing education programs and qualifications.

**Key Details**:
- **Official Site**: https://uis.unesco.org/en/topic/international-standard-classification-education-isced
- **Data Mapping Portal**: https://isced.uis.unesco.org/data-mapping/
- **Current Version**: ISCED 2011
- **Structure**: 9 education levels (expanded from 7)

**Data Access**:
- **Mapping Downloads**: Spreadsheet formats (.xlsx, .xls)
- **Coverage**: 100+ countries
- **Revisions**: ISCED 1997 and ISCED 2011 available
- **API Access**: No documented API (contact UNESCO UIS)

**Companion Classification**:
- **ISCED-F 2013**: Fields of Education and Training classification

### 5.3 Back4App CIP Codes Database

**Description**: Third-party CIP codes database with API access.

**Key Details**:
- **URL**: https://www.back4app.com/database/back4app/cip-codes-instructional-programs
- **Authentication**: API key required
- **Data Format**: JSON
- **Coverage**: Complete CIP classification system

## 6. Major University APIs That Expose Program Catalogs

### 6.1 Stanford University - Student RESTful Web Services

**Description**: API for retrieving student and course data.

**Key Details**:
- **Documentation**: https://uit.stanford.edu/developers/apis/student
- **Authentication**: Valid certificate required
- **Data Format**: XML responses
- **Base URL**: https://studentws.stanford.edu/v1/

**Key Endpoints**:
1. **Person Information**: `/person/{personId}`
2. **Enrollment Data**: 
   - Current term: `/person/{personId}/enrollment/term`
   - Specific term: `/person/{personId}/enrollment/term/{termId}`
3. **Course/Class Information**:
   - Course class: `/courseclass/{courseClassId}`
   - Course details: `/courseclass/{courseClassId}/course`
   - Class details: `/class/{classId}`

**Search Capabilities**:
- Search students by qualifier, career, academic ID
- Search classes by term and subject/academic ID
- Multiple identifier support (univid, sunetid, regid)

### 6.2 Harvard University - API Platform and Data Resources

**Description**: Comprehensive API platform for Harvard developers.

**Key Details**:
- **Platform URL**: https://www.huit.harvard.edu/api-platform-services
- **Data Resources**: https://data.harvard.edu/apis
- **Authentication**: Varies by API
- **Coverage**: Library metadata, course data, institutional resources

**Available APIs**:
1. **Course Planner API**: Harvard College/GSAS student course management
2. **Harvard Library APIs**: Catalog metadata and Presto Data Lookup service
3. **Harvard Art Museums API**: Collections data
4. **General API Platform**: For building and publishing APIs

**Library API Features**:
- **Presto Data Lookup**: RESTful web API for library systems
- **Data Formats**: XML and JSON responses
- **License**: Broad use licenses for catalog metadata

### 6.3 University of Waterloo - Open Data API

**Description**: Comprehensive open data platform with 40+ methods and 80+ datasets.

**Key Details**:
- **API Portal**: https://uwaterloo.ca/api/
- **Documentation**: https://openapi.data.uwaterloo.ca/api-docs/index.html
- **Version**: v3 (registration required for API key)
- **GitHub Support**: https://github.com/uWaterloo/OpenData
- **Data Scope**: Publicly visible data only

**Platform Features**:
- 40+ API methods for various datasets
- Authoritative, approved, and timely datasets
- Registration required for API access
- Comprehensive documentation and GitHub support

### 6.4 MIT OpenCourseWare

**Description**: Open access to MIT course materials.

**Key Details**:
- **URL**: https://ocw.mit.edu/
- **Launch**: 2001
- **Coverage**: 2,500+ courses and resources
- **Access**: Free and open to the world
- **API Status**: No documented API (web interface and downloads)

**Additional Platforms**:
- YouTube channel with 450M+ views
- Refreshed website (2022)
- Open course content available for download

### 6.5 Open Course API Project

**Description**: Open-source initiative for college course data APIs.

**Key Details**:
- **GitHub**: https://github.com/OpenCourseAPI
- **Website**: https://opencourse.dev
- **Mission**: "Empowering students to build data-driven applications"
- **Location**: San Francisco Bay Area

**Key Repositories**:
1. **OpenCourseAPI**: Main API for college course data scraping
2. **OwlAPI**: REST API for Foothill/De Anza courses
3. **live-fhda-class-data**: Auto-updated course data
4. **OpenCourseBot**: Discord bot for college information

**Technical Stack**:
- **Primary Language**: Python
- **License**: MIT
- **Focus**: Community colleges (Foothill/De Anza)

## 7. Integration Opportunities for Career Guidance Platforms

### 7.1 Recommended Primary Data Sources

**For Canadian Focus**:
1. **Statistics Canada CIP 2021**: Official classification system with open data access
2. **ESDC CPIC Database**: Comprehensive Canadian program database (contact required)
3. **Quebec BCI Services**: Quebec-specific university coordination data

**For International Coverage**:
1. **College Scorecard API**: Comprehensive US institution data
2. **HESA Open Data**: UK higher education statistics
3. **ETER Database**: European higher education institutions

### 7.2 Technical Integration Recommendations

**API-First Approach**:
- **College Scorecard API**: Ready-to-use REST API with comprehensive US data
- **University of Waterloo API**: Canadian institutional model
- **Urban Institute Education Data API**: Multi-language support (Python, R, JavaScript)

**Data Download and Processing**:
- **Statistics Canada CIP**: CSV downloads for classification mapping
- **ISCED UNESCO**: Spreadsheet downloads for international standardization
- **HESA Open Data**: Creative Commons licensed UK data

**Hybrid Approaches**:
- **Primary APIs**: College Scorecard, Waterloo, Urban Institute
- **Classification Systems**: CIP Canada, ISCED for standardization
- **Supplementary Data**: University-specific APIs (Stanford, Harvard)

### 7.3 Authentication and Rate Limiting Considerations

**No Authentication Required**:
- Statistics Canada Open Data
- HESA Open Data (CC BY 4.0)
- Coursera Catalog APIs (beta)
- Universities List API

**API Key Required**:
- College Scorecard API (apply online)
- University of Waterloo API (registration)
- Back4App CIP Database

**Institutional Access Required**:
- Stanford Student API (certificate)
- Harvard Course Planner API (enrolled students)
- HESA Heidi Plus (premium access)

### 7.4 Data Quality and Update Frequencies

**Regular Updates**:
- **College Scorecard**: Annual updates
- **ESDC CPIC**: Yearly updates
- **HESA**: Annual academic year updates

**Periodic Revisions**:
- **CIP Canada**: 10-year cycle (next ~2031)
- **ISCED UNESCO**: Periodic revisions
- **CIP NCES**: 10-year cycle (next 2030)

**Real-Time/Frequent**:
- **University APIs**: Term-based or real-time updates
- **Course APIs**: Semester/term-based updates

## 8. Implementation Roadmap for Career Guidance Integration

### Phase 1: Foundation (Immediate Implementation)
1. **College Scorecard API Integration**: US institutional data
2. **Statistics Canada CIP**: Canadian program classification
3. **Universities List API**: Basic global university directory

### Phase 2: Enhanced Coverage (3-6 months)
1. **University of Waterloo API**: Canadian institutional model
2. **Urban Institute Education Data API**: Advanced US data access
3. **HESA Open Data Integration**: UK coverage

### Phase 3: Comprehensive International (6-12 months)
1. **ETER Database Integration**: European coverage
2. **TEQSA National Register**: Australian institutions
3. **ISCED Mapping**: International standardization

### Phase 4: Specialized APIs (12+ months)
1. **University-Specific APIs**: Stanford, Harvard, MIT
2. **Regional Databases**: Quebec BCI, specialized platforms
3. **Real-Time Course Data**: Open Course API, institution-specific

## 9. Contact Information and Support

### Government Sources
- **Statistics Canada**: infostats@statcan.gc.ca
- **ESDC Canada**: Contact through EduCanada platform
- **UNESCO ISCED**: UIS support channels

### Technical Support
- **University of Waterloo API**: https://github.com/uWaterloo/OpenData/issues
- **College Scorecard**: Through Data.gov support
- **Urban Institute**: Documentation portal support

### Community Resources
- **Open Course API**: https://github.com/OpenCourseAPI
- **University API Documentation**: Institution-specific support channels

---

## Conclusion

This research identifies numerous actionable data sources for university program information, ranging from comprehensive government databases to specialized institutional APIs. The recommended approach involves implementing high-availability APIs first (College Scorecard, University of Waterloo) while building classification mapping using standard systems (CIP, ISCED). The integration opportunities are substantial, with clear paths for both rapid implementation and comprehensive international coverage.

For career guidance platforms like Orientor, the combination of official government data sources (Statistics Canada, ESDC) with robust APIs (College Scorecard, Waterloo) provides an excellent foundation for program recommendation systems, while international sources (HESA, ETER) enable global expansion capabilities.