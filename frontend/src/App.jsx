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
    const [currentTrack, setCurrentTrack] = useState(null);

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

    const handleRecommendations = async (trackId) => {
        try {
            console.log('Sending request for recommendations...');  // Registro
            const response = await fetch('http://127.0.0.1:5002/recommend_knn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    track_id: trackId,
                    top_k: 5,  // Número de vecinos más cercanos que queremos recuperar
                }),
            });

            console.log('Received response:', response);  // Registro de la respuesta

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error);
            }

            const data = await response.json();
            console.log('Response data:', data);  // Registro de los datos

            // Verifica la respuesta del servidor
            if (!data.recommendations) {
                throw new Error("Invalid response from server");
            }

            const detailedRecommendations = await Promise.all(data.recommendations.map(async rec => {
                try {
                    const trackResponse = await fetch(`http://127.0.0.1:5001/track_info?track_id=${rec.track_id}`);
                    if (!trackResponse.ok) {
                        const error = await trackResponse.json();
                        throw new Error(error.error);
                    }
                    const trackData = await trackResponse.json();
                    return { ...trackData, distance: rec.distance, album_cover: rec.album_cover, track_url: `http://127.0.0.1:5001/audio?track_id=${rec.track_id}` };
                } catch (error) {
                    console.error(`Error fetching track info for ${rec.track_id}:`, error);
                    return null;
                }
            }));

            // Filtrar resultados nulos
            setRecommendations(detailedRecommendations.filter(rec => rec !== null));
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            alert(`Error fetching recommendations: ${error.message}`);
        }
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
                            <Results
                                results={results}
                                onRecommend={handleRecommendations}
                                setPlayingTrack={setPlayingTrack}
                                indexingMethod={indexingMethod}
                                currentTrack={currentTrack}
                                setCurrentTrack={setCurrentTrack}
                            />
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
                            <Recommendations
                                recommendations={recommendations}
                                setPlayingTrack={setPlayingTrack}
                                handleIdentify={handleIdentify}
                            />
                        </Paper>
                    </Grid>
                </Grid>
            </Container>
        </ThemeProvider>
    );
};

export default App;
