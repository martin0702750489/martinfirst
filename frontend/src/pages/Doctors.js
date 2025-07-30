import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Doctors = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Doctor Management
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Doctor Profiles & Schedules
          </Typography>
          <Typography color="text.secondary">
            This page will contain doctor registration, specializations, schedules, and 
            availability management. Includes doctor profiles and consultation fees.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Doctors;