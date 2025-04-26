import { Box, CircularProgress, Container, Typography } from '@mui/material';

export default function Loading() {
  return (
    <Container maxWidth="md" sx={{ py: 8 }}>
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '50vh' 
      }}>
        <CircularProgress size={60} thickness={4} />
        <Typography variant="h6" sx={{ mt: 4 }}>
          Loading career suggestions...
        </Typography>
      </Box>
    </Container>
  );
} 