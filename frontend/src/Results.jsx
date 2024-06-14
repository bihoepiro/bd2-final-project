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

    if (results.length === 0) return null;

    const topResult = results[0];
    const otherResults = results.slice(1);

    return (
        <div className="results-container">
            <div className="top-result">
                <MusicNoteIcon style={{ fontSize: 100, color: '#1DB954' }} />
                <h2>{topResult.title}</h2>
                <p>{topResult.lyrics}</p>
            </div>
            <div className="other-results">
                {otherResults.map((result, index) => (
                    <Accordion
                        key={index}
                        expanded={expanded === `panel${index}`}
                        onChange={handleExpansion(`panel${index}`)}
                        TransitionComponent={Fade}
                        TransitionProps={{ timeout: 400 }}
                        className="result-item"
                        style={{ backgroundColor: '#282828', borderRadius: '8px' }}
                    >
                        <AccordionSummary
                            expandIcon={<ExpandMoreIcon style={{ color: '#1DB954' }} />}
                            aria-controls={`panel${index}-content`}
                            id={`panel${index}-header`}
                        >
                            <MusicNoteIcon style={{ fontSize: 50, color: '#1DB954', marginRight: '10px' }} />
                            <div className="result-info">
                                <Typography variant="h6" style={{ color: '#1DB954', margin: 0 }}>
                                    {result.title}
                                </Typography>
                            </div>
                            <span className="result-duration">{result.duration}</span>
                        </AccordionSummary>
                        <AccordionDetails style={{ backgroundColor: '#282828', color: '#fff' }}>
                            <Typography>
                                {result.lyrics}
                            </Typography>
                        </AccordionDetails>
                    </Accordion>
                ))}
            </div>
        </div>
    );
};

export default Results;
