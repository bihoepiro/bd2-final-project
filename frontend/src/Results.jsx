import React from 'react';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Fade from '@mui/material/Fade';

const Results = ({ results }) => {
    const [expanded, setExpanded] = React.useState(false);

    const handleExpansion = (panel) => (event, isExpanded) => {
        setExpanded(isExpanded ? panel : false);
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

    const topResult = results[0];
    const otherResults = results.slice(1);

    return (
        <div className="results-container">
            <Accordion
                expanded={expanded === 'panel0'}
                onChange={handleExpansion('panel0')}
                TransitionComponent={Fade}
                TransitionProps={{ timeout: 400 }}
                className="result-item"
                style={{ backgroundColor: '#282828', borderRadius: '8px', marginBottom: '10px' }}
            >
                <AccordionSummary
                    expandIcon={<ExpandMoreIcon style={{ color: '#1DB954' }} />}
                    aria-controls="panel0-content"
                    id="panel0-header"
                >
                    <MusicNoteIcon style={{ fontSize: 50, color: '#1DB954', marginRight: '10px' }} />
                    <div className="result-info">
                        <Typography variant="h4" style={{ color: '#1DB954', margin: 0 }}>
                            {topResult.track_name}
                        </Typography>
                        <Typography variant="body2" style={{ color: '#fff' }}>
                            {formatDuration(topResult.duration_ms)}
                        </Typography>
                    </div>
                </AccordionSummary>
                <AccordionDetails style={{ backgroundColor: '#282828', color: '#fff' }}>
                    <Typography>
                        {truncateLyrics(topResult.lyrics, 250)}
                    </Typography>
                </AccordionDetails>
            </Accordion>
            <div className="other-results">
                {otherResults.map((result, index) => (
                    <Accordion
                        key={index}
                        expanded={expanded === `panel${index + 1}`}
                        onChange={handleExpansion(`panel${index + 1}`)}
                        TransitionComponent={Fade}
                        TransitionProps={{ timeout: 400 }}
                        className="result-item"
                        style={{ backgroundColor: '#282828', borderRadius: '8px', marginBottom: '10px' }}
                    >
                        <AccordionSummary
                            expandIcon={<ExpandMoreIcon style={{ color: '#1DB954' }} />}
                            aria-controls={`panel${index + 1}-content`}
                            id={`panel${index + 1}-header`}
                        >
                            <MusicNoteIcon style={{ fontSize: 50, color: '#1DB954', marginRight: '10px' }} />
                            <div className="result-info">
                                <Typography variant="h5" style={{ color: '#1DB954', margin: 0 }}>
                                    {result.track_name}
                                </Typography>
                                <Typography variant="body2" style={{ color: '#fff' }}>
                                    {formatDuration(result.duration_ms)}
                                </Typography>
                                <Typography variant="body2" style={{ color: '#fff' }}>
                                    {result.rank}
                                </Typography>

                            </div>
                        </AccordionSummary>
                        <AccordionDetails style={{ backgroundColor: '#282828', color: '#fff' }}>
                            <Typography>
                                {truncateLyrics(result.lyrics, 250)}
                            </Typography>
                        </AccordionDetails>
                    </Accordion>
                ))}
            </div>
        </div>
    );
};

export default Results;
