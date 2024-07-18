import React, { useRef, useState, useEffect } from 'react';
import { Box, Typography, Button, Paper, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import PlayCircleOutlineRoundedIcon from '@mui/icons-material/PlayCircleOutlineRounded';
import MicIcon from '@mui/icons-material/Mic';
import { CSSTransition } from 'react-transition-group';
import './animations.css';

const Recommendations = ({ recommendations, setPlayingTrack, handleIdentify, handleMethodChange, method }) => {
    const nodeRefs = useRef([]);
    const [isRecording, setIsRecording] = useState(false);
    const [mediaRecorder, setMediaRecorder] = useState(null);
    const [audioChunks, setAudioChunks] = useState([]);
    const [currentAudio, setCurrentAudio] = useState(null);

    const handleRecord = async () => {
        if (isRecording) {
            mediaRecorder.stop();
            setIsRecording(false);
        } else {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            setMediaRecorder(recorder);

            recorder.ondataavailable = (event) => {
                setAudioChunks((prevChunks) => [...prevChunks, event.data]);
            };

            recorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioUrl = URL.createObjectURL(audioBlob);
                console.log('Audio Blob:', audioBlob);
                console.log('Audio URL:', audioUrl);
                handleIdentify(audioUrl, audioBlob);
                setAudioChunks([]);
            };

            recorder.start();
            setIsRecording(true);

            setTimeout(() => {
                if (recorder.state === 'recording') {
                    recorder.stop();
                    setIsRecording(false);
                }
            }, 10000); // Graba durante 10 segundos
        }
    };

    const handlePlay = (trackUrl) => {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
        }
        const newAudio = new Audio(trackUrl);
        setCurrentAudio(newAudio);
        newAudio.play();
        setPlayingTrack(trackUrl);
    };

    const truncateLyrics = (lyrics, maxLength) => {
        if (!lyrics) return '';  // Añadir manejo de casos undefined
        if (lyrics.length > maxLength) {
            return lyrics.substring(0, maxLength) + '...';
        }
        return lyrics;
    };

    useEffect(() => {
        return () => {
            if (currentAudio) {
                currentAudio.pause();
                currentAudio.currentTime = 0;
            }
        };
    }, [currentAudio]);

    return (
        <Box>
            <Button
                onClick={handleRecord}
                style={{
                    color: '#fff',
                    backgroundColor: isRecording ? '#f44336' : '#1DB954',
                    borderRadius: '50%',
                    padding: '10px',
                    minWidth: '50px',
                    minHeight: '50px',
                    marginBottom: '20px',
                }}
            >
                <MicIcon style={{ fontSize: 30 }} />
            </Button>

            <FormControl variant="outlined" fullWidth style={{ marginBottom: '20px', minWidth: '120px' }}>
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
                    <MenuItem value="KNN-HighD">KNN-HighD</MenuItem>
                    <MenuItem value="KNN-RTree">KNN-RTree</MenuItem>
                </Select>
            </FormControl>

            {recommendations.map((rec, index) => (
                <CSSTransition
                    key={index}
                    in={true}
                    appear={true}
                    timeout={300}
                    classNames="fade"
                    nodeRef={nodeRefs.current[index] || (nodeRefs.current[index] = React.createRef())}
                >
                    <Paper
                        ref={nodeRefs.current[index]}
                        style={{
                            backgroundColor: '#282828',
                            padding: '10px',
                            marginBottom: '10px',
                            borderRadius: '8px',
                            display: 'flex',
                            alignItems: 'center'
                        }}
                    >
                        <img
                            src={rec.album_cover}
                            alt={`${rec.track_name} cover`}
                            style={{ width: '60px', height: '60px', borderRadius: '4px', marginRight: '10px' }}
                        />
                        <Box flexGrow={1}>
                            <Typography variant="h6" style={{ color: '#1DB954' }}>
                                {rec.track_name}
                            </Typography>
                            <Typography variant="body2" style={{ color: '#fff' }}>
                                {rec.artist_name}
                            </Typography>
                            <Typography variant="body2" style={{ color: '#aaa' }}>
                                {rec.album_name} • {rec.release_date}
                            </Typography>
                            <Typography variant="body2" style={{ color: '#ddd', marginTop: '10px' }}>
                                {truncateLyrics(rec.lyrics, 200)}
                            </Typography>
                        </Box>
                        <Button
                            onClick={() => handlePlay(rec.track_url)}
                            style={{
                                color: '#fff',
                                backgroundColor: 'transparent',
                                borderRadius: '50%',
                                padding: 0,
                                minWidth: '40px',
                                minHeight: '40px'
                            }}
                        >
                            <PlayCircleOutlineRoundedIcon style={{ fontSize: 40, color: '#1DB954' }} />
                        </Button>
                    </Paper>
                </CSSTransition>
            ))}
        </Box>
    );
};

export default Recommendations;
