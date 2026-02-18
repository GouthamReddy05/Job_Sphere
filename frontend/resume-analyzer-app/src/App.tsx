import React, { useState, useEffect } from 'react';
import { Shield, BookOpen, Lightbulb, MessageCircle, Clock, Eye, EyeOff, Upload, MapPin, Briefcase, Calendar, User, Mail, Lock, ChevronRight, FileText, Target, Zap } from 'lucide-react';

// --- Types ---

interface User {
  email: string;
  password: string;
}

interface job {
  title: string;
  company: string;
  location: string;
  link: string;
}

interface FormData {
  jobRole: string;
  location: string;
  experience: string;
  resume: File | null;
  jobDescription: string;
}

interface Feature {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}

interface Project {
  title: string;
  objective: string;
  tools: string;
  skills: string;
}

interface AnalysisResult {
  title: string;
  score?: number;
  details?: string[];
  skills?: string[];
  projects?: Project[];
  questions?: string[];
  jobs?: job[];
}

// --- Constants & Helper Functions ---

const STORAGE_KEY = 'resume_analyzer_users';

const indianCities = [
  'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad',
  'Jaipur', 'Surat', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal',
  'Visakhapatnam', 'Pimpri', 'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra',
  'Nashik', 'Faridabad', 'Meerut', 'Rajkot', 'Kalyan', 'Vasai', 'Varanasi',
  'Srinagar', 'Aurangabad', 'Dhanbad', 'Amritsar', 'Navi Mumbai', 'Allahabad',
  'Ranchi', 'Howrah', 'Coimbatore', 'Jabalpur', 'Gwalior', 'Vijayawada', 'Jodhpur',
  'Madurai', 'Raipur', 'Kota', 'Guwahati', 'Chandigarh', 'Solapur', 'Hubballi'
];

const features: Feature[] = [
  {
    id: 'ats-score',
    icon: <Shield className="w-8 h-8" />,
    title: 'Job Match Analysis',
    description: 'Optimize for automated screening systems',
    color: 'from-blue-500 to-purple-600'
  },
  {
    id: 'missing-skills',
    icon: <BookOpen className="w-8 h-8" />,
    title: 'Missing Skills',
    description: 'Identify gaps in your profile',
    color: 'from-purple-500 to-pink-600'
  },
  {
    id: 'project-ideas',
    icon: <Lightbulb className="w-8 h-8" />,
    title: 'Project Ideas',
    description: 'Build to stand out',
    color: 'from-pink-500 to-red-600'
  },
  {
    id: 'interview-prep',
    icon: <MessageCircle className="w-8 h-8" />,
    title: 'Interview Prep',
    description: 'Practice with real questions',
    color: 'from-green-500 to-teal-600'
  },
  {
    id: 'job-matches',
    icon: <Clock className="w-8 h-8" />,
    title: 'Live Job Links',
    description: 'Find relevant openings',
    color: 'from-yellow-500 to-orange-600'
  }
];


const initializeUsers = (): User[] => {
  try {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    }
  } catch (error) {
    console.warn('Could not load users from localStorage');
  }
  return [];
};

const saveUsers = (users: User[]) => {
  try {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
    }
  } catch (error) {
    console.warn('Could not save users to localStorage');
  }
};

const AIResumeAnalyzer: React.FC = () => {
  // State Management
  const [currentPage, setCurrentPage] = useState<'auth' | 'dashboard' | 'analysis'>('auth');
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  // const [users, setUsers] = useState<User[]>(initializeUsers()); // Removed local users
  const [currentUser, setCurrentUser] = useState<string>('');
  const [selectedFeature, setSelectedFeature] = useState<string>('');

  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [dashboardForm, setDashboardForm] = useState<FormData>({
    jobRole: '',
    location: '',
    experience: '',
    resume: null,
    jobDescription: '',
  });

  const [locationSuggestions, setLocationSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [dashboardErrors, setDashboardErrors] = useState<Record<string, string>>({});

  // Persist users to localStorage whenever the users state changes -- REMOVED
  // useEffect(() => {
  //   saveUsers(users);
  // }, [users]);

  // --- Auth Functions ---

  const validateEmail = (email: string): boolean => {
    return email.endsWith("@gmail.com") || email.endsWith(".edu.in");
  };

  const handleTabSwitch = (loginMode: boolean) => {
    setIsLogin(loginMode);
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setError('');
    setSuccess('');
  };

  const handleLogin = async () => {
    const validationError = 'Please use a @gmail.com or .edu.in email address.';
    if (!email || !password) {
      setError('Please enter email and password.');
      return;
    }
    if (!validateEmail(email)) {
      setError(validationError);
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/login`, {
        method: 'POST',
        credentials: "include",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        // If it's a 401/400 error, it might still return JSON
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
          const data = await response.json();
          throw new Error(data.detail || 'Login failed');
        } else {
          throw new Error('Login failed');
        }
      }

      // Successful login redirects to /dashboard (which returns HTML)
      // fetch follows redirect, so response.url should eventually contain 'dashboard'
      // Or simply assume success if status is 200 (after following redirect)

      setCurrentUser(email);
      setCurrentPage('dashboard');
      setEmail('');
      setPassword('');
      setError('');
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleSignup = async () => {
    const validationError = 'Please use a @gmail.com or .edu.in email address.';
    if (!email || !password || !confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }
    if (!validateEmail(email)) {
      setError(validationError);
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/signup`, {
        method: 'POST',
        credentials: "include",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
          const data = await response.json();
          throw new Error(data.detail || 'Signup failed');
        } else {
          throw new Error('Signup failed');
        }
      }

      // Signup successful, redirecting to login...
      setIsLogin(true);
      setSuccess('Account created! Please login.');
      setError('');
      setPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${process.env.REACT_APP_API_URL}/api/auth/logout`, { method: 'POST', credentials: "include" });
    } catch (e) {
      console.error("Logout failed", e);
    }

    setCurrentUser('');
    setCurrentPage('auth');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setError('');
    setSuccess('');
    setDashboardForm({
      jobRole: '',
      location: '',
      experience: '',
      resume: null,
      jobDescription: '',
    });
    setDashboardErrors({});
    setIsLogin(true);
    setAnalysisResult(null);
    setSelectedFeature('');
  };

  // --- Dashboard & Form Functions ---

  const filterCities = (input: string) => {
    if (!input) return [];
    return indianCities.filter(city =>
      city.toLowerCase().startsWith(input.toLowerCase())
    ).slice(0, 5);
  };

  const handleLocationChange = (value: string) => {
    setDashboardForm(prev => ({ ...prev, location: value }));
    const suggestions = filterCities(value);
    setLocationSuggestions(suggestions);
    setShowSuggestions(suggestions.length > 0);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (allowedTypes.includes(file.type)) {
        setDashboardForm(prev => ({ ...prev, resume: file }));
        setDashboardErrors(prev => ({ ...prev, resume: '' }));
      } else {
        setDashboardForm(prev => ({ ...prev, resume: null }));
        setDashboardErrors(prev => ({ ...prev, resume: 'Only PDF and DOCX files are allowed.' }));
      }
    }
  };

  const validateDashboardForm = (featureId: string) => {
    const errors: Record<string, string> = {};
    if (!dashboardForm.jobRole.trim()) errors.jobRole = 'Please enter the job role.';
    if (!dashboardForm.location.trim()) errors.location = 'Please enter the location.';
    if (!dashboardForm.experience) errors.experience = 'Please select your experience.';
    if (!dashboardForm.resume) errors.resume = 'Please upload your resume.';
    if (featureId === 'ats-score' && !dashboardForm.jobDescription.trim()) {
      errors.jobDescription = 'Job Description is required for Job Match Analysis.';
    }
    setDashboardErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // --- API Call & Analysis Function ---

  const handleFeatureClick = async (featureId: string) => {
    if (!validateDashboardForm(featureId)) {
      return;
    }

    setIsLoading(true);
    setError('');
    setAnalysisResult(null);
    setSelectedFeature(featureId);

    const apiFormData = new FormData();
    apiFormData.append('jobRole', dashboardForm.jobRole);
    apiFormData.append('location', dashboardForm.location);
    apiFormData.append('experience', dashboardForm.experience);
    apiFormData.append('resume', dashboardForm.resume as Blob);
    apiFormData.append('jobDescription', dashboardForm.jobDescription);

    try {
      // Step 1: Process the resume and basic info
      const processResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/process-resume`, {
        method: 'POST',
        credentials: 'include',
        body: apiFormData,
      });

      if (!processResponse.ok) {
        const errorData = await processResponse.json();
        throw new Error(errorData.error || 'Failed to process resume.');
      }
      const processedData = await processResponse.json();

      // Step 2: Send processed data for specific analysis
      const analysisPayload = {
        resume_text: processedData.resume_text,
        job_role: processedData.job_role,
        job_description: dashboardForm.jobDescription,
        location: dashboardForm.location, // Added location for job matching
      };

      const analyzeResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/analyze/${featureId}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(analysisPayload),
      });

      if (!analyzeResponse.ok) {
        const errorData = await analyzeResponse.json();
        throw new Error(errorData.error || `Failed to get analysis for ${featureId}.`);
      }
      const analysisData = await analyzeResponse.json();

      setAnalysisResult(analysisData);
      setCurrentPage('analysis');

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Render Functions ---

  const renderAuthPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl p-8 border border-white/20">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full mb-4">
              <FileText className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">JobSphere</h1>
            <p className="text-purple-200">Optimize your career with AI insights</p>
          </div>

          <div className="flex bg-white/10 rounded-xl p-1 mb-6">
            <button
              onClick={() => handleTabSwitch(true)}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${isLogin ? 'bg-white text-purple-900 shadow-sm' : 'text-white hover:bg-white/10'}`}
            >
              Login
            </button>
            <button
              onClick={() => handleTabSwitch(false)}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${!isLogin ? 'bg-white text-purple-900 shadow-sm' : 'text-white hover:bg-white/10'}`}
            >
              Sign Up
            </button>
          </div>

          <div className="space-y-6">
            <div>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-purple-300" />
                <input type="email" placeholder="Enter your email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all" />
              </div>
            </div>
            <div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-purple-300" />
                <input type={showPassword ? 'text' : 'password'} placeholder="Enter your password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full pl-12 pr-12 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all" />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 transform -translate-y-1/2 text-purple-300 hover:text-white transition-colors">
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
            {!isLogin && (
              <div>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-purple-300" />
                  <input type="password" placeholder="Confirm your password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all" />
                </div>
              </div>
            )}
            {success && <div className="text-green-400 text-sm text-center bg-green-500/10 p-3 rounded-lg">{success}</div>}
            {error && <div className="text-red-400 text-sm text-center bg-red-500/10 p-3 rounded-lg">{error}</div>}
            <button onClick={isLogin ? handleLogin : handleSignup} className="w-full bg-gradient-to-r from-purple-500 to-blue-500 text-white py-3 px-6 rounded-xl font-semibold hover:from-purple-600 hover:to-blue-600 transform hover:scale-[1.02] transition-all duration-200 shadow-lg">
              {isLogin ? 'Login to Account' : 'Create New Account'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderDashboardPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <nav className="bg-white/10 backdrop-blur-md border-b border-white/20 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">JobSphere</h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <User className="w-5 h-5 text-purple-200" />
              <span className="text-purple-200">{currentUser}</span>
            </div>
            <button onClick={handleLogout} className="text-purple-200 hover:text-white transition-colors text-sm">Logout</button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Welcome back!</h2>
          <p className="text-purple-200">Let's analyze your resume and boost your career prospects</p>
        </div>

        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 mb-8 hover:bg-white/15 transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/10">
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <span>Your Information</span>
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-purple-200 mb-2">Job Role</label>
              <div className="relative">
                <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-purple-300" />
                <input type="text" placeholder="e.g., Frontend Developer" value={dashboardForm.jobRole} onChange={(e) => setDashboardForm(prev => ({ ...prev, jobRole: e.target.value }))} className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all" />
              </div>
              {dashboardErrors.jobRole && <p className="text-red-400 text-sm mt-1">{dashboardErrors.jobRole}</p>}
            </div>
            <div className="relative">
              <label className="block text-sm font-medium text-purple-200 mb-2">Location</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-purple-300" />
                <input type="text" placeholder="Start typing city name..." value={dashboardForm.location} onChange={(e) => handleLocationChange(e.target.value)} onFocus={() => setShowSuggestions(locationSuggestions.length > 0)} onBlur={() => setTimeout(() => setShowSuggestions(false), 200)} className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all" />
                {showSuggestions && locationSuggestions.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-white/95 backdrop-blur-md rounded-lg shadow-lg border border-purple-200 z-10">
                    {locationSuggestions.map((city, index) => (
                      <button key={index} onClick={() => { setDashboardForm(prev => ({ ...prev, location: city })); setShowSuggestions(false); }} className="w-full text-left px-4 py-3 hover:bg-purple-100 text-gray-800 transition-colors first:rounded-t-lg last:rounded-b-lg">
                        {city}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {dashboardErrors.location && <p className="text-red-400 text-sm mt-1">{dashboardErrors.location}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-purple-200 mb-2">Experience</label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-purple-300" />
                <select value={dashboardForm.experience} onChange={(e) => setDashboardForm(prev => ({ ...prev, experience: e.target.value }))} className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all">
                  <option value="" className="bg-purple-900">Select experience</option>
                  <option value="0-1" className="bg-purple-900">0-1 years</option>
                  <option value="1-3" className="bg-purple-900">1-3 years</option>
                  <option value="3-5" className="bg-purple-900">3-5 years</option>
                  <option value="5-10" className="bg-purple-900">5-10 years</option>
                  <option value="10+" className="bg-purple-900">10+ years</option>
                </select>
              </div>
              {dashboardErrors.experience && <p className="text-red-400 text-sm mt-1">{dashboardErrors.experience}</p>}
            </div>
            <div className="lg:col-span-3">
              <label className="block text-sm font-medium text-purple-200 mb-2">Job Description <span className="text-purple-300">(Required for Job Match Analysis)</span></label>
              <div className="relative">
                <FileText className="absolute left-3 top-4 w-5 h-5 text-purple-300" />
                <textarea placeholder="Paste the job description here..." value={dashboardForm.jobDescription} onChange={(e) => setDashboardForm(prev => ({ ...prev, jobDescription: e.target.value }))} className="w-full h-28 pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-y" />
              </div>
              {dashboardErrors.jobDescription && <p className="text-red-400 text-sm mt-1">{dashboardErrors.jobDescription}</p>}
            </div>
          </div>
          <div className="mt-6">
            <label className="block text-sm font-medium text-purple-200 mb-2">Upload Resume</label>
            <div className="relative">
              <input type="file" accept=".pdf,.docx" onChange={handleFileUpload} className="hidden" id="resume-upload" />
              <label htmlFor="resume-upload" className="flex items-center justify-center w-full py-6 px-4 border-2 border-dashed border-white/30 rounded-xl cursor-pointer hover:border-purple-400 transition-colors">
                <div className="text-center">
                  <Upload className="w-12 h-12 text-purple-300 mx-auto mb-3" />
                  <p className="text-purple-200 font-medium">{dashboardForm.resume ? dashboardForm.resume.name : 'Click to upload resume'}</p>
                  <p className="text-purple-300 text-sm mt-1">PDF or DOCX files only</p>
                </div>
              </label>
            </div>
            {dashboardErrors.resume && <p className="text-red-400 text-sm mt-1">{dashboardErrors.resume}</p>}
          </div>
        </div>

        {isLoading && <p className="text-center text-purple-200 mb-4">Analyzing your resume, please wait...</p>}
        {error && <p className="text-center text-red-400 mb-4 bg-red-500/10 p-3 rounded-lg">{error}</p>}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {features.map((feature) => (
            <div key={feature.id} onClick={() => !isLoading && handleFeatureClick(feature.id)} className={`group bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 transform transition-all duration-300 ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-105 hover:shadow-2xl'}`}>
              <div className={`w-16 h-16 bg-gradient-to-r ${feature.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <div className="text-white">{feature.icon}</div>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-purple-200 text-sm mb-4">{feature.description}</p>
              <div className="flex items-center text-purple-300 group-hover:text-white transition-colors">
                <span className="text-sm font-medium">Click to analyze</span>
                <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAnalysisPage = () => {
    const feature = features.find(f => f.id === selectedFeature);

    if (isLoading) {
      return <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center text-white text-2xl">Analyzing...</div>;
    }
    if (!analysisResult) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex flex-col items-center justify-center text-white p-4">
          <p className="text-xl mb-4">No analysis data found.</p>
          <button onClick={() => setCurrentPage('dashboard')} className="bg-gradient-to-r from-purple-500 to-blue-500 text-white py-2 px-6 rounded-lg font-semibold">
            Go Back
          </button>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        <nav className="bg-white/10 backdrop-blur-md border-b border-white/20 p-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button onClick={() => setCurrentPage('dashboard')} className="text-purple-200 hover:text-white transition-colors p-2 rounded-md">← Back</button>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center"><FileText className="w-6 h-6 text-white" /></div>
                <h1 className="text-2xl font-bold text-white">JobSphere</h1>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-4xl mx-auto p-6">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
            <div className="flex items-center mb-6">
              <div className={`w-16 h-16 bg-gradient-to-r ${feature?.color} rounded-xl flex items-center justify-center mr-4`}>
                <div className="text-white">{feature?.icon}</div>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{analysisResult.title}</h2>
                <p className="text-purple-200">Analysis Results</p>
              </div>
            </div>

            <div className="space-y-6">
              {analysisResult.score !== undefined && (
                <div className="bg-white/10 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-lg font-semibold text-white">Overall Score</span>
                    <span className="text-3xl font-bold text-green-400">{analysisResult.score}%</span>
                  </div>
                  <div className="w-full bg-white/20 rounded-full h-3">
                    <div className="bg-gradient-to-r from-green-400 to-blue-500 h-3 rounded-full transition-all duration-1000" style={{ width: `${analysisResult.score}%` }}></div>
                  </div>
                </div>
              )}
              {analysisResult.details && (
                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Detailed Analysis</h3>
                  <div className="space-y-3">
                    {analysisResult.details.map((detail, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <Target className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                        <p className="text-purple-200">{detail}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {analysisResult.skills && (
                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Skills to Add</h3>
                  {analysisResult.skills.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {analysisResult.skills.map((skill, index) => (
                        <div key={index} className="bg-purple-500/20 rounded-lg p-3 border border-purple-300/30">
                          <div className="flex items-center space-x-2">
                            <Zap className="w-4 h-4 text-yellow-400" />
                            <span className="text-white font-medium">{skill}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-purple-200">Your skills are well-aligned. No missing skills found.</p>
                  )}
                </div>
              )}
              {analysisResult.projects && (
                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Recommended Projects</h3>
                  {analysisResult.projects.length > 0 ? (
                    <div className="space-y-4">
                      {analysisResult.projects.map((project, index) => (
                        <div key={index} className="bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-lg p-4 border border-white/20">
                          <p className="font-bold text-white mb-2">{index + 1}. {project.title || 'Untitled Project'}</p>
                          <p className="text-sm text-purple-200 mb-2"><strong className="text-purple-100">Objective:</strong> {project.objective || 'Not available'}</p>
                          <p className="text-sm text-purple-200 mb-2"><strong className="text-purple-100">Tech Stack:</strong> {project.tools || 'Not available'}</p>
                          <p className="text-sm text-purple-200"><strong className="text-purple-100">Skills:</strong> {project.skills || 'Not available'}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-purple-200">No specific project ideas generated for this role.</p>
                  )}
                </div>
              )}
              {analysisResult.questions && (
                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Common Interview Questions</h3>
                  <div className="space-y-4">
                    {analysisResult.questions.map((question, index) => (
                      <div key={index} className="bg-white/10 rounded-lg p-4 border border-white/20">
                        <div className="flex items-start space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-teal-500 rounded-lg flex items-center justify-center flex-shrink-0">
                            <MessageCircle className="w-4 h-4 text-white" />
                          </div>
                          <p className="text-white">{question}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {analysisResult.jobs && Array.isArray(analysisResult.jobs) && (
                <div className="bg-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Job Opportunities</h3>
                  <div className="space-y-4">
                    {/* 👇 USE THIS CORRECTED MAPPING LOGIC 👇 */}
                    {analysisResult.jobs.map((job, index) => (
                      <a key={index} href={job.link} target="_blank" rel="noopener noreferrer" className="block bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-lg p-4 border border-white/20 hover:scale-[1.02] transition-transform cursor-pointer">
                        <div className="flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            {/* Correct: Render specific properties like job.title, not the whole job object */}
                            <p className="text-white font-semibold truncate">{job.title}</p>
                            <div className="flex items-center text-sm text-purple-200 mt-1">
                              <Briefcase className="w-4 h-4 mr-2 flex-shrink-0" />
                              <span className="truncate">{job.company}</span>
                            </div>
                            <div className="flex items-center text-sm text-purple-200 mt-1">
                              <MapPin className="w-4 h-4 mr-2 flex-shrink-0" />
                              <span className="truncate">{job.location}</span>
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-orange-400 ml-4 flex-shrink-0" />
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className="mt-8 flex justify-center">
              <button onClick={() => setCurrentPage('dashboard')} className="bg-gradient-to-r from-purple-500 to-blue-500 text-white py-3 px-8 rounded-xl font-semibold hover:from-purple-600 hover:to-blue-600 transform hover:scale-[1.02] transition-all duration-200 shadow-lg">
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Main Page Router
  switch (currentPage) {
    case 'auth':
      return renderAuthPage();
    case 'dashboard':
      return renderDashboardPage();
    case 'analysis':
      return renderAnalysisPage();
    default:
      return renderAuthPage();
  }
};

export default AIResumeAnalyzer;