import React, { useState } from 'react';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  Paper,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:5001';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      console.log('Sending search request for:', query);
      const response = await axios.post('/search', { query }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      console.log('Received response:', response.data);
      
      if (response.data.error) {
        setError(response.data.error);
      } else if (response.data.vacancies && response.data.vacancies.length === 0) {
        setError('No vacancies found for your query');
      } else {
        setResults(response.data);
      }
    } catch (err) {
      console.error('Error details:', err);
      setError(
        err.response?.data?.error || 
        'Error fetching results. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          HH.ru Parser
        </Typography>
        
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="Enter search query"
              variant="outlined"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              disabled={loading}
              placeholder="e.g. Python Developer"
            />
            <Button
              variant="contained"
              onClick={handleSearch}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {results && results.vacancies && results.vacancies.length > 0 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Search Results ({results.vacancies.length} vacancies found)
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Position</TableCell>
                    <TableCell>Company</TableCell>
                    <TableCell>Salary</TableCell>
                    <TableCell>Experience</TableCell>
                    <TableCell>Skills</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {results.vacancies.map((vacancy, index) => (
                    <TableRow key={index}>
                      <TableCell>{vacancy.name}</TableCell>
                      <TableCell>{vacancy.employer}</TableCell>
                      <TableCell>{vacancy.salary}</TableCell>
                      <TableCell>{vacancy.experience}</TableCell>
                      <TableCell>{vacancy.skills.join(', ')}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}
      </Box>
    </Container>
  );
}

export default App; 