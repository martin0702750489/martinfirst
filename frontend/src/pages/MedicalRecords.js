import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const MedicalRecords = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Medical Records
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Patient Medical History & Records
          </Typography>
          <Typography color="text.secondary">
            This page will contain patient medical records, diagnoses, treatments,
            prescriptions, and medical history tracking with secure access controls.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MedicalRecords;