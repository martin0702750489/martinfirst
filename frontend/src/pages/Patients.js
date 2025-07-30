import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Patients = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Patient Management
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Patient List & Management
          </Typography>
          <Typography color="text.secondary">
            This page will contain patient registration, search, and management functionality.
            Features include patient profiles, medical history, and contact information.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Patients;