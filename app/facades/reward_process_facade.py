from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..repositories.report_repository import ReportRepository
from ..repositories.post_repository import PostRepository
from ..repositories.user_repository import UserRepository
from ..schemas.report_schema import ReportResponse


class RewardProcessFacade:
    """
    Simple facade to coordinate the reward process workflow.
    
    This facade only handles coordination - all actual work is done
    by existing repository methods.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.report_repo = ReportRepository(db)
        self.post_repo = PostRepository(db)
        self.user_repo = UserRepository(db)
    
    def execute_reward_process(self, report_id: int) -> ReportResponse:
        """
        Coordinate the reward process by calling existing repository methods.
        
        Steps:
        1. Get report and validate it exists
        2. Get related post and transfer reward points (if any)
        3. Mark post as found
        4. Mark report as rewarded
        """
        try:
            # Get and validate report exists (using existing method)
            report = self.report_repo.get_report_by_id(report_id)
            if not report:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Report with id {report_id} not found"
                )
            
            # Get related post for reward points (using existing method)
            post = self.post_repo.get_post_by_id(report.post_id)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Related post not found"
                )
            
            # Transfer reward points if available (minimal coordination logic)
            if post.rewards and post.rewards[0].amount > 0:
                reward_amount = post.rewards[0].amount
                reporter = self.user_repo.get_user_by_id(report.reporter_id)
                if not reporter:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Reporter not found"
                    )
                
                # Update balance using existing method
                new_balance = reporter.balance + reward_amount
                if not self.user_repo.update_user_balance(report.reporter_id, new_balance):
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update reporter balance"
                    )
            
            # Mark post as found (using existing method)
            if not self.post_repo.mark_post_as_found(report.post_id):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to mark post as found"
                )
            
            # Mark report as rewarded (using existing method)
            updated_report = self.report_repo.reward_report(report_id)
            if not updated_report:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to reward report"
                )
            
            return ReportResponse.from_report(updated_report)
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing reward: {str(e)}"
            )