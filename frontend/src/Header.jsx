import React from 'react';
import { AppBar, Toolbar, TextField, Button, Select, MenuItem, FormControl, InputLabel, CircularProgress } from '@mui/material';

const Header = ({ query, setQuery, topK, setTopK, indexingMethod, setIndexingMethod, handleSearch, loading }) => {
    return (
        <AppBar position="static" color="primary">
            <Toolbar>
                <TextField
                    label="Enter your query"
                    variant="outlined"
                    size="small"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    style={{ backgroundColor: '#fff', borderRadius: '4px', marginRight: '10px' }}
                    InputLabelProps={{
                        style: { color: '#000' },
                    }}
                    InputProps={{
                        style: { color: '#000' },
                    }}
                />
                <TextField
                    label="Top K"
                    type="number"
                    variant="outlined"
                    size="small"
                    value={topK}
                    onChange={(e) => setTopK(e.target.value)}
                    style={{ backgroundColor: '#fff', borderRadius: '4px', marginRight: '10px' }}
                    InputLabelProps={{
                        style: { color: '#000' },
                    }}
                    InputProps={{
                        style: { color: '#000' },
                    }}
                />
                <FormControl variant="outlined" size="small" style={{ marginRight: '10px', backgroundColor: '#fff', borderRadius: '4px' }}>
                    <InputLabel style={{ color: '#000' }}>Indexing Method</InputLabel>
                    <Select
                        value={indexingMethod}
                        onChange={(e) => setIndexingMethod(e.target.value)}
                        label="Indexing Method"
                        MenuProps={{
                            PaperProps: {
                                style: {
                                    backgroundColor: '#282828',
                                    color: '#fff',
                                },
                            },
                        }}
                        style={{ color: '#000' }}
                    >
                        <MenuItem value="Custom Implementation">Custom Implementation</MenuItem>
                        <MenuItem value="PostgreSQL">PostgreSQL</MenuItem>
                    </Select>
                </FormControl>
                <Button variant="contained" color="primary" onClick={handleSearch} disabled={loading}>
                    {loading ? <CircularProgress size={24} /> : 'Search'}
                </Button>
            </Toolbar>
        </AppBar>
    );
};

export default Header;
