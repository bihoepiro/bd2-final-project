import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        primary: {
            main: '#1DB954',
        },
        background: {
            default: '#121212',
        },
        text: {
            primary: '#ffffff',
        }
    },
    typography: {
        fontFamily: 'Arial, sans-serif',
        h5: {
            fontWeight: 600,
        },
        h6: {
            fontWeight: 500,
        },
        body2: {
            fontSize: '0.9rem',
        },
    },
    components: {
        MuiAppBar: {
            styleOverrides: {
                root: {
                    marginBottom: '20px',
                    borderRadius: '8px',
                    padding: '10px',
                    margin: '10px',
                    backgroundColor: '#1DB954',
                },
            },
        },
        MuiToolbar: {
            styleOverrides: {
                root: {
                    display: 'flex',
                    justifyContent: 'space-between',
                },
            },
        },
        MuiTextField: {
            styleOverrides: {
                root: {
                    margin: '0 10px',
                    backgroundColor: '#fff',
                    borderRadius: '4px',
                },
                input: {
                    color: '#000',
                },
                label: {
                    color: '#000',
                },
            },
        },
        MuiSelect: {
            styleOverrides: {
                root: {
                    color: '#000',
                },
                icon: {
                    color: '#000',
                },
            },
        },
        MuiMenu: {
            styleOverrides: {
                paper: {
                    backgroundColor: '#282828',
                    color: '#fff',
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    backgroundColor: '#1DB954',
                    color: '#fff',
                    '&:hover': {
                        backgroundColor: '#1ed760',
                    },
                },
            },
        },
    },
});

export default theme;
