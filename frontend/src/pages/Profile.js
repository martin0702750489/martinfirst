import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Profile = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        User Profile
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Profile Settings & Information
          </Typography>
          <Typography color="text.secondary">
            This page will contain user profile information, settings, password change,
            and role-specific information management.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Profile;