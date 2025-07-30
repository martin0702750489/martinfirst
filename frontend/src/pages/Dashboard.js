import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Button,
  Paper,
  Divider,
} from '@mui/material';
import {
  People as PeopleIcon,
  LocalHospital as DoctorIcon,
  CalendarToday as CalendarIcon,
  Assignment as AssignmentIcon,
  TrendingUp as TrendingUpIcon,
  AccessTime as TimeIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const StatCard = ({ title, value, icon, color, subtitle }) => (
  <Card sx={{ height: '100%', display: 'flex', alignItems: 'center' }}>
    <CardContent sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography color="text.secondary" gutterBottom variant="body2">
            {title}
          </Typography>
          <Typography variant="h4" component="div" fontWeight="bold">
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        <Avatar sx={{ bgcolor: color, width: 56, height: 56 }}>
          {icon}
        </Avatar>
      </Box>
    </CardContent>
  </Card>
);

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, api } = useAuth();
  const [stats, setStats] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsResponse, dashboardResponse] = await Promise.all([
        api.get('/dashboard/quick-stats'),
        api.get('/dashboard/my-dashboard'),
      ]);
      
      setStats(statsResponse.data);
      setDashboardData(dashboardResponse.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      scheduled: 'primary',
      confirmed: 'success',
      completed: 'info',
      cancelled: 'error',
      in_progress: 'warning',
    };
    return colors[status] || 'default';
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Welcome back, {user?.first_name}!
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Here's what's happening at the hospital today.
      </Typography>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Appointments"
            value={stats?.today_appointments || 0}
            icon={<CalendarIcon />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Appointments"
            value={stats?.pending_appointments || 0}
            icon={<TimeIcon />}
            color="warning.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Patients"
            value={stats?.total_active_patients || 0}
            icon={<PeopleIcon />}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Doctors"
            value={stats?.total_active_doctors || 0}
            icon={<DoctorIcon />}
            color="info.main"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Role-specific content */}
        {user?.role === 'patient' && dashboardData?.patient_info && (
          <>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    My Upcoming Appointments
                  </Typography>
                  {dashboardData.upcoming_appointments?.length > 0 ? (
                    <List>
                      {dashboardData.upcoming_appointments.map((appointment, index) => (
                        <ListItem key={appointment.id} divider={index < dashboardData.upcoming_appointments.length - 1}>
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: 'primary.main' }}>
                              <CalendarIcon />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={`Dr. ${appointment.doctor.user.first_name} ${appointment.doctor.user.last_name}`}
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {new Date(appointment.appointment_date).toLocaleDateString()} at{' '}
                                  {appointment.appointment_time}
                                </Typography>
                                <Chip
                                  label={appointment.status}
                                  size="small"
                                  color={getStatusColor(appointment.status)}
                                  sx={{ mt: 0.5 }}
                                />
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography color="text.secondary">No upcoming appointments</Typography>
                  )}
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="outlined"
                      onClick={() => navigate('/appointments')}
                      fullWidth
                    >
                      View All Appointments
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Medical Records
                  </Typography>
                  {dashboardData.recent_medical_records?.length > 0 ? (
                    <List>
                      {dashboardData.recent_medical_records.map((record, index) => (
                        <ListItem key={record.id} divider={index < dashboardData.recent_medical_records.length - 1}>
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: 'success.main' }}>
                              <AssignmentIcon />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={record.diagnosis || 'General Consultation'}
                            secondary={new Date(record.visit_date).toLocaleDateString()}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography color="text.secondary">No medical records yet</Typography>
                  )}
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="outlined"
                      onClick={() => navigate('/medical-records')}
                      fullWidth
                    >
                      View Medical History
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}

        {user?.role === 'doctor' && dashboardData?.doctor_info && (
          <>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Today's Schedule
                  </Typography>
                  {dashboardData.today_appointments?.length > 0 ? (
                    <List>
                      {dashboardData.today_appointments.map((appointment, index) => (
                        <ListItem key={appointment.id} divider={index < dashboardData.today_appointments.length - 1}>
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: 'primary.main' }}>
                              <CalendarIcon />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={`${appointment.patient.user.first_name} ${appointment.patient.user.last_name}`}
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {appointment.appointment_time} - {appointment.reason || 'General consultation'}
                                </Typography>
                                <Chip
                                  label={appointment.status}
                                  size="small"
                                  color={getStatusColor(appointment.status)}
                                  sx={{ mt: 0.5 }}
                                />
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography color="text.secondary">No appointments today</Typography>
                  )}
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="outlined"
                      onClick={() => navigate('/appointments')}
                      fullWidth
                    >
                      View All Appointments
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Patients
                  </Typography>
                  {dashboardData.recent_patients?.length > 0 ? (
                    <List>
                      {dashboardData.recent_patients.map((patient, index) => (
                        <ListItem key={patient.id} divider={index < dashboardData.recent_patients.length - 1}>
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: 'success.main' }}>
                              <PeopleIcon />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={`${patient.user.first_name} ${patient.user.last_name}`}
                            secondary={`Patient ID: ${patient.patient_id}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography color="text.secondary">No recent patients</Typography>
                  )}
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="outlined"
                      onClick={() => navigate('/patients')}
                      fullWidth
                    >
                      View All Patients
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}

        {/* Quick Actions for Admin/Staff */}
        {['admin', 'receptionist', 'nurse'].includes(user?.role) && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      variant="outlined"
                      fullWidth
                      onClick={() => navigate('/patients')}
                      startIcon={<PeopleIcon />}
                    >
                      Manage Patients
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      variant="outlined"
                      fullWidth
                      onClick={() => navigate('/doctors')}
                      startIcon={<DoctorIcon />}
                    >
                      Manage Doctors
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      variant="outlined"
                      fullWidth
                      onClick={() => navigate('/appointments')}
                      startIcon={<CalendarIcon />}
                    >
                      Schedule Appointment
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      variant="outlined"
                      fullWidth
                      onClick={() => navigate('/medical-records')}
                      startIcon={<AssignmentIcon />}
                    >
                      Medical Records
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default Dashboard;