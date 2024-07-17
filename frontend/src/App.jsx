import React, { useState } from 'react';
import { Container, CssBaseline, Box, Grid, Typography, Paper, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import Results from './Results';
import Header from './Header';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import Recommendations from './Recommendations';
import theme from './theme';

const App = () => {
    const [query, setQuery] = useState('');
    const [topK, setTopK] = useState(10);
    const [indexingMethod, setIndexingMethod] = useState('Custom Implementation');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [queryTime, setQueryTime] = useState(0);
    const [recommendations, setRecommendations] = useState([]);
    const [method, setMethod] = useState('KNN-Secuencial');
    const [playingTrack, setPlayingTrack] = useState(null);

    const handleSearch = async () => {
        setLoading(true);
        const startTime = performance.now();

        try {
            const response = await fetch('http://127.0.0.1:5001/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query,
                    topK,
                    indexingMethod,
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error);
            }

            const data = await response.json();
            const endTime = performance.now();
            setQueryTime(endTime - startTime);

            setResults(data.results);
        } catch (error) {
            console.error('Error during search:', error);
            alert(`Error during search: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleRecommendations = (trackId) => {
        // Simulate recommendations logic
        const simulatedRecommendations = [
            {
                track_name: "Song 1",
                artist_name: "Artist 1",
                album_name: "Album 1",
                release_date: "2021-01-01",
                album_cover: "https://via.placeholder.com/60",
                track_url: "URL1"
            },
            {
                track_name: "Song 2",
                artist_name: "Artist 2",
                album_name: "Album 2",
                release_date: "2021-02-01",
                album_cover: "https://via.placeholder.com/60",
                track_url: "URL2"
            },
            {
                track_name: "Song 3",
                artist_name: "Artist 3",
                album_name: "Album 3",
                release_date: "2021-03-01",
                album_cover: "https://via.placeholder.com/60",
                track_url: "URL3"
            },
        ];
        setRecommendations(simulatedRecommendations);
    };

    const handleIdentify = (blobUrl, blob) => {
        // Simulated identified song data
        const identifiedSong = {
            track_name: 'Simulated Song',
            artist_name: 'Simulated Artist',
            album_name: 'Simulated Album',
            release_date: '2021-01-01',
            album_cover: 'https://via.placeholder.com/60',
            track_url: blobUrl,
        };
        setRecommendations([identifiedSong]);
    };

    const handleMethodChange = (event) => {
        setMethod(event.target.value);
    };

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Container maxWidth={false} style={{ padding: '20px' }}>
                <Header
                    query={query}
                    setQuery={setQuery}
                    topK={topK}
                    setTopK={setTopK}
                    indexingMethod={indexingMethod}
                    setIndexingMethod={setIndexingMethod}
                    handleSearch={handleSearch}
                    loading={loading}
                />
                {queryTime > 0 && (
                    <Box display="flex" alignItems="center" justifyContent="center" className="query-time" style={{ color: '#fff', marginBottom: '20px' }}>
                        <Typography variant="body1" gutterBottom>
                            Query Time: {queryTime.toFixed(2)} ms
                        </Typography>
                        <AccessTimeIcon style={{ fontSize: 20, color: '#1DB954', marginLeft: '8px' }} />
                    </Box>
                )}
                <Grid container spacing={2}>
                    <Grid item xs={8}>
                        {results.length === 0 ? (
                            <Box display="flex" alignItems="center" justifyContent="center" style={{ color: '#fff', marginTop: '50px' }}>
                                <Typography variant="h5">No results found. Please enter a query to search for songs.</Typography>
                            </Box>
                        ) : (
                            <Results results={results} onRecommend={handleRecommendations} setPlayingTrack={setPlayingTrack} />
                        )}
                    </Grid>
                    <Grid item xs={4}>
                        <Paper style={{ padding: '20px', backgroundColor: '#121212', borderRadius: '8px' }}>
                            <Typography variant="h5" gutterBottom style={{ color: '#1DB954' }}>
                                Recommended Songs
                            </Typography>
                            <FormControl variant="outlined" fullWidth style={{ marginBottom: '20px' }}>
                                <InputLabel id="method-select-label" style={{ color: '#fff' }}>Test Method</InputLabel>
                                <Select
                                    labelId="method-select-label"
                                    value={method}
                                    onChange={handleMethodChange}
                                    label="Test Method"
                                    style={{ color: '#fff' }}
                                    MenuProps={{
                                        PaperProps: {
                                            style: {
                                                backgroundColor: '#282828',
                                                color: '#fff',
                                            },
                                        },
                                    }}
                                >
                                    <MenuItem value="KNN-Secuencial">KNN-Secuencial</MenuItem>
                                    <MenuItem value="KNN-RTree">KNN-RTree</MenuItem>
                                    <MenuItem value="KNN-HighD">KNN-HighD</MenuItem>
                                </Select>
                            </FormControl>
                            <Recommendations recommendations={recommendations} setPlayingTrack={setPlayingTrack} handleIdentify={handleIdentify} />
                        </Paper>
                    </Grid>
                </Grid>
                {playingTrack && (
                    <audio controls autoPlay style={{ width: '100%', marginTop: '20px' }}>
                        <source src={playingTrack} type="audio/mpeg" />
                        Your browser does not support the audio element.
                    </audio>
                )}
            </Container>
        </ThemeProvider>
    );
};

export default App;
