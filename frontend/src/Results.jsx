import React, { useState, useEffect, useRef } from 'react';
import { Accordion, AccordionSummary, AccordionDetails, Typography, Button, Box } from '@mui/material';
import ExpandMoreRoundedIcon from '@mui/icons-material/ExpandMoreRounded';
import PlayCircleOutlineRoundedIcon from '@mui/icons-material/PlayCircleOutlineRounded';
import QueueMusicRoundedIcon from '@mui/icons-material/QueueMusicRounded';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import { CSSTransition } from 'react-transition-group';
import './animations.css';

const Results = ({ results, onRecommend, setPlayingTrack, indexingMethod, currentTrack, setCurrentTrack }) => {
    const [expanded, setExpanded] = useState(false);
    const [activeIndex, setActiveIndex] = useState(null);
    const nodeRefs = useRef([]);

    const handleExpansion = (panel) => (event, isExpanded) => {
        setExpanded(isExpanded ? panel : false);
    };

    const handlePlay = async (trackId, index) => {
        if (!trackId) {
            console.error("Error: trackId is undefined");
            return;
        }
        const trackUrl = `http://127.0.0.1:5001/audio?track_id=${trackId}&indexingMethod=${indexingMethod}`;

        if (currentTrack) {
            currentTrack.pause();
        }

        const newAudio = new Audio(trackUrl);
        newAudio.play();
        setCurrentTrack(newAudio);

        setPlayingTrack(trackUrl);
        setActiveIndex(index);
    };

    const formatDuration = (duration_ms) => {
        return (duration_ms / 60000).toFixed(2) + ' min';
    };

    const truncateLyrics = (lyrics, maxLength) => {
        if (lyrics.length > maxLength) {
            return lyrics.substring(0, maxLength) + '...';
        }
        return lyrics;
    };

    if (results.length === 0) return null;

    return (
        <Box>
            {results.map((result, index) => (
                <Accordion
                    key={index}
                    expanded={expanded === `panel${index}`}
                    onChange={handleExpansion(`panel${index}`)}
                    style={{ backgroundColor: '#282828', borderRadius: '8px', marginBottom: '10px' }}
                >
                    <AccordionSummary
                        expandIcon={<ExpandMoreRoundedIcon style={{ color: '#1DB954' }} />}
                        aria-controls={`panel${index}-content`}
                        id={`panel${index}-header`}
                    >
                        <Box
                            component="span"
                            sx={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                width: '60px',
                                height: '60px',
                                borderRadius: '4px',
                                marginRight: '10px',
                                backgroundColor: result.album_cover ? 'transparent' : '#444',
                            }}
                        >
                            {result.album_cover ? (
                                <img src={result.album_cover} alt={`${result.track_name} cover`} style={{ width: '60px', height: '60px', borderRadius: '4px' }} />
                            ) : (
                                <MusicNoteIcon style={{ fontSize: 50, color: '#1DB954' }} />
                            )}
                        </Box>
                        <Box>
                            <Typography variant="h5" style={{ color: '#1DB954', margin: 0 }}>
                                {result.track_name}
                            </Typography>
                            <Typography variant="body2" style={{ color: '#fff' }}>
                                {result.track_artist}
                            </Typography>
                        </Box>
                        <Box marginLeft="auto" display="flex" alignItems="center">
                            <Button
                                onClick={() => onRecommend(result.track_id)}
                                style={{
                                    color: '#fff',
                                    backgroundColor: 'transparent',
                                    borderRadius: '50%',
                                    padding: 0,
                                    minWidth: '40px',
                                    minHeight: '40px',
                                    marginRight: '10px'
                                }}
                            >
                                <QueueMusicRoundedIcon style={{ fontSize: 40, color: '#1DB954' }} />
                            </Button>
                            <Button
                                onClick={() => handlePlay(result.track_id, index)}
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
                        </Box>
                    </AccordionSummary>
                    <AccordionDetails style={{ backgroundColor: '#282828', color: '#fff' }}>
                        <CSSTransition
                            in={expanded === `panel${index}`}
                            timeout={300}
                            classNames="fade"
                            unmountOnExit
                            nodeRef={nodeRefs.current[index] || (nodeRefs.current[index] = React.createRef())}
                        >
                            <div ref={nodeRefs.current[index]}>
                                <Typography>
                                    {truncateLyrics(result.lyrics, 250)}
                                </Typography>
                            </div>
                        </CSSTransition>
                    </AccordionDetails>
                </Accordion>
            ))}
        </Box>
    );
};

export default Results;
