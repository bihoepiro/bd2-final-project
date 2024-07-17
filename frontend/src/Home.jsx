import React from 'react';
import { Button, Container, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import './homebackground.css';

const Home = () => {
    const navigate = useNavigate();

    const handleEnter = () => {
        navigate('/search');
    };

    return (
        <div className="home-background">
            <Container
                maxWidth="sm"
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: '30vh',
                    textAlign: 'center',
                    backgroundColor: 'rgba(0, 0, 0, 0.3)',
                    padding: '20px',
                    borderRadius: '30px'
                }}
            >
                <Typography variant="h2" gutterBottom sx={{ fontFamily: 'Arial, sans-serif' }}>
                    Bienvenido!
                </Typography>
                <Box mt={4}>
                    <Button variant="contained" style={{ backgroundColor: '#1DB954', color: '#fff' }} onClick={handleEnter} size="large">
                        Ingresar
                    </Button>
                </Box>
            </Container>
        </div>
    );
};

export default Home;
