import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import Meeting
from app.models.enums import MeetingStatus, ProcessingStatus


class TestMeetingAPI:
    """Test cases for meeting API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_meeting(self, client: AsyncClient, sample_meeting_data):
        """Test creating a new meeting."""
        response = await client.post("/api/v1/meetings/", json=sample_meeting_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_meeting_data["title"]
        assert data["description"] == sample_meeting_data["description"]
        assert data["participants"] == sample_meeting_data["participants"]
        assert data["status"] == MeetingStatus.SCHEDULED
        assert data["processing_status"] == ProcessingStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_get_meeting(self, client: AsyncClient, db_session: AsyncSession, sample_meeting_data):
        """Test retrieving a meeting by ID."""
        # Create a meeting
        meeting = Meeting(**sample_meeting_data)
        db_session.add(meeting)
        await db_session.commit()
        await db_session.refresh(meeting)
        
        # Get the meeting
        response = await client.get(f"/api/v1/meetings/{meeting.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(meeting.id)
        assert data["title"] == meeting.title
    
    @pytest.mark.asyncio
    async def test_list_meetings(self, client: AsyncClient, db_session: AsyncSession):
        """Test listing meetings with pagination."""
        # Create multiple meetings
        for i in range(5):
            meeting = Meeting(
                title=f"Meeting {i}",
                description=f"Description {i}",
                participants=[f"user{i}@example.com"],
            )
            db_session.add(meeting)
        await db_session.commit()
        
        # Get meetings list
        response = await client.get("/api/v1/meetings/?limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5
        assert data["limit"] == 3
    
    @pytest.mark.asyncio
    async def test_update_meeting(self, client: AsyncClient, db_session: AsyncSession, sample_meeting_data):
        """Test updating a meeting."""
        # Create a meeting
        meeting = Meeting(**sample_meeting_data)
        db_session.add(meeting)
        await db_session.commit()
        await db_session.refresh(meeting)
        
        # Update the meeting
        update_data = {"title": "Updated Meeting Title"}
        response = await client.patch(f"/api/v1/meetings/{meeting.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Meeting Title"
    
    @pytest.mark.asyncio
    async def test_delete_meeting(self, client: AsyncClient, db_session: AsyncSession, sample_meeting_data):
        """Test soft deleting a meeting."""
        # Create a meeting
        meeting = Meeting(**sample_meeting_data)
        db_session.add(meeting)
        await db_session.commit()
        await db_session.refresh(meeting)
        
        # Delete the meeting
        response = await client.delete(f"/api/v1/meetings/{meeting.id}")
        
        assert response.status_code == 200
        
        # Verify meeting is not found
        response = await client.get(f"/api/v1/meetings/{meeting.id}")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_meeting(self, client: AsyncClient):
        """Test getting a non-existent meeting."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        response = await client.get(f"/api/v1/meetings/{fake_id}")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_meeting_validation(self, client: AsyncClient):
        """Test meeting creation with invalid data."""
        invalid_data = {"description": "Missing title"}
        response = await client.post("/api/v1/meetings/", json=invalid_data)
        
        assert response.status_code == 422